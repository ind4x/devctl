import xml.etree.ElementTree as ET

from devctl.generators.spring import patch_pom_xml


def test_patch_pom_xml(tmp_path):
    """Verify that patch_pom_xml correctly injects JJWT and MapStruct dependencies."""
    # Setup: Create a minimal pom.xml
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    pom_path = project_dir / "pom.xml"

    initial_pom = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>
	<groupId>com.example</groupId>
	<artifactId>demo</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<dependencies>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter</artifactId>
		</dependency>
	</dependencies>
</project>
"""
    pom_path.write_text(initial_pom)

    # Run
    patch_pom_xml(str(project_dir))

    # Verify
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    tree = ET.parse(str(pom_path))
    root = tree.getroot()

    # Check dependencies
    deps = root.findall(".//m:dependency", ns)
    artifacts = [d.find("m:artifactId", ns).text for d in deps]

    assert "jjwt-api" in artifacts
    assert "jjwt-impl" in artifacts
    assert "jjwt-jackson" in artifacts
    assert "mapstruct" in artifacts

    # Check annotation processors
    processors = root.findall(".//m:annotationProcessorPaths/m:path/m:artifactId", ns)
    processor_names = [p.text for p in processors]
    assert "lombok" in processor_names
    assert "lombok-mapstruct-binding" in processor_names
    assert "mapstruct-processor" in processor_names
