from pathlib import Path

from devctl.generators.agent.generator import generate_agent_context


def test_generate_agent_context_in_empty_dir(tmp_path: Path):
    result = generate_agent_context(tmp_path)
    assert result is True

    agents_file = tmp_path / "AGENTS.md"
    claude_file = tmp_path / "CLAUDE.md"
    cursor_file = tmp_path / ".cursorrules"

    assert agents_file.exists()
    assert claude_file.exists()
    assert cursor_file.exists()

    content = agents_file.read_text(encoding="utf-8")
    assert "No active microservices detected yet" in content
    assert "devctl run" in content
    assert "devctl tui" in content
    assert "devctl add resource" in content


def test_generate_agent_context_with_services_and_db(tmp_path: Path):
    # Setup mock Spring project
    api_dir = tmp_path / "api"
    api_dir.mkdir()
    (api_dir / "pom.xml").write_text("<project></project>", encoding="utf-8")

    props_dir = api_dir / "src" / "main" / "resources"
    props_dir.mkdir(parents=True)
    (props_dir / "application.properties").write_text("server.port=8081\n", encoding="utf-8")

    compose_file = api_dir / "docker-compose-db.yml"
    compose_file.write_text(
        """
services:
  api-db:
    image: postgres:15
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: custom_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: secret_password
""",
        encoding="utf-8",
    )

    # Setup mock Angular project
    front_dir = tmp_path / "front"
    front_dir.mkdir()
    (front_dir / "angular.json").write_text("{}", encoding="utf-8")
    (front_dir / "package.json").write_text('{"name": "front"}', encoding="utf-8")

    result = generate_agent_context(tmp_path)
    assert result is True

    agents_content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "api" in agents_content
    assert "Spring Boot" in agents_content
    assert "8081" in agents_content
    assert "./mvnw test" in agents_content

    assert "front" in agents_content
    assert "Angular" in agents_content
    assert "4200" in agents_content

    assert "api-db" in agents_content
    assert "PostgreSQL" in agents_content
    assert "5433" in agents_content
    assert "custom_db" in agents_content
    assert "test_user" in agents_content
    assert "secret_password" in agents_content


def test_generate_agent_context_invalid_path():
    result = generate_agent_context("/non/existent/path/devctl_test_dummy")
    assert result is False
