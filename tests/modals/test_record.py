import pytest
from unittest import mock

# from bagels.modals import record
from bagels.models.account import Account
from bagels.models.category import Category, Nature
from bagels.managers import record_templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bagels.models.database.db import Base
import bagels.modals.record as record
import bagels.managers.record_templates as rt

import sys
import types
import pytest


# Create a fake CONFIG object with the right shape
class DummyHotkeys:
    class RecordModal:
        new_split = "ctrl+n"
        new_paid_split = "ctrl+p"
        delete_last_split = "ctrl+d"
        submit_and_template = "ctrl+s"

    record_modal = RecordModal()


class DummyConfig:
    hotkeys = DummyHotkeys()


sys.modules["bagels.config"] = types.SimpleNamespace(CONFIG=DummyConfig())

from bagels.modals import record


# Setup test database
@pytest.fixture(scope="function")
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def setup_test_engine(monkeypatch, engine):
    # Replace the global engine with our test engine
    import bagels.managers.record_templates as rt

    rt.Session = sessionmaker(bind=engine)
    yield


@pytest.fixture
def account(session):
    account = Account(name="Test Account", beginningBalance=1000.0)
    session.add(account)
    session.commit()
    return account


@pytest.fixture
def category(session):
    category = Category(name="Test Category", nature=Nature.WANT, color="#000000")
    session.add(category)
    session.commit()
    return category


@pytest.fixture
def template_data(account, category):
    return {
        "label": "Test Template",
        "amount": 100.0,
        "accountId": account.id,
        "categoryId": category.id,
        "isIncome": False,
        "isTransfer": False,
        "transferToAccountId": None,
    }


def test_create_template(template_data):
    template = record_templates.create_template(template_data)
    assert template.label == template_data["label"]
    assert template.amount == template_data["amount"]
    assert template.accountId == template_data["accountId"]
    assert template.categoryId == template_data["categoryId"]
    assert template.order == 1  # First template should have order 1


@pytest.fixture
def record_modal(monkeypatch, is_editing):
    monkeypatch.setattr(record, "get_all_persons", lambda: [])
    monkeypatch.setattr(record, "get_all_accounts_with_balance", lambda: [])
    split_form = record.RecordForm()
    return record.RecordModal(
        title="Test Record Modal",
        splitForm=split_form,
        isEditing=is_editing,
    )


@pytest.mark.parametrize("is_editing", [True, False])
def test_action_add_split(record_modal):
    initial_split_count = record_modal.splitCount
    record_modal.action_add_split()
    assert record_modal.splitCount == initial_split_count + 1
    assert (
        len(record_modal.splitForm)
        == record_modal.splitFormOneLength * record_modal.splitCount
    )


@pytest.mark.parametrize("is_editing", [True, False])
def test_action_add_paid_split(record_modal):
    initial_split_count = record_modal.splitCount
    record_modal.action_add_paid_split()
    assert record_modal.splitCount == initial_split_count + 1


@pytest.mark.parametrize("is_editing", [True, False])
def test_action_delete_last_split(record_modal):
    record_modal.action_add_split()  # Ensure at least one split
    initial_split_count = record_modal.splitCount
    record_modal.action_delete_last_split()
    assert record_modal.splitCount == max(initial_split_count - 1, 0)


def test_action_submit_and_template(record_modal):
    with mock.patch.object(record_modal, "action_submit") as mock_submit:
        record_modal.action_submit_and_template()
        assert record_modal.shift_pressed is True
        mock_submit.assert_called_once()


def test_action_submit(record_modal):
    pass


def test_action_submit_success(record_modal):
    with (
        mock.patch(
            "bagels.modals.record.validateForm",
            side_effect=[({"label": "ok"}, {}, True), ({"split": "ok"}, {}, True)],
        ) as mock_validate,
        mock.patch.object(record_modal, "dismiss") as mock_dismiss,
    ):
        record_modal.action_submit()

        assert mock_validate.call_count == 2
        mock_dismiss.assert_called_once()
        args, kwargs = mock_dismiss.call_args
        assert "record" in args[0]
        assert "splits" in args[0]
