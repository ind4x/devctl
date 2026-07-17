import os

from devctl.utils.env_loader import get_project_env, load_env_file


def test_load_env_file_missing(tmp_path):
    assert load_env_file(tmp_path) == {}


def test_load_env_file_basic(tmp_path):
    env_content = "DB_URL=postgres://localhost:5432/db\nAPI_KEY=secret_key\n"
    (tmp_path / ".env").write_text(env_content)

    expected = {"DB_URL": "postgres://localhost:5432/db", "API_KEY": "secret_key"}
    assert load_env_file(tmp_path) == expected


def test_load_env_file_advanced(tmp_path):
    env_content = (
        "# This is a comment\n"
        "  SPACED_KEY = spaced_value  \n"
        'QUOTED_VAL="double_quoted"\n'
        "SINGLE_QUOTED='single_quoted'\n"
        "\n"
        "EMPTY_VAL=\n"
    )
    (tmp_path / ".env").write_text(env_content)

    expected = {
        "SPACED_KEY": "spaced_value",
        "QUOTED_VAL": "double_quoted",
        "SINGLE_QUOTED": "single_quoted",
        "EMPTY_VAL": "",
    }
    assert load_env_file(tmp_path) == expected


def test_get_project_env(tmp_path):
    (tmp_path / ".env").write_text("TEST_VAR=from_dotenv")

    # Pre-set a system var
    os.environ["SYSTEM_VAR"] = "from_system"

    env = get_project_env(tmp_path)

    assert env["TEST_VAR"] == "from_dotenv"
    assert env["SYSTEM_VAR"] == "from_system"
    # Ensure it's a copy of system env plus the new var
    assert "PATH" in env
