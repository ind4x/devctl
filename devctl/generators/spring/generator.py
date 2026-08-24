"""
Generators for Spring Boot projects.
Includes boilerplate downloading via Spring Initializr and POM patching.
"""

import io
import os
import stat
import xml.etree.ElementTree as ET
import zipfile

import requests
import typer

from .scaffolder import generate_spring_security


def patch_pom_xml(project_path: str):
    """
    Surgically adds missing JJWT and MapStruct dependencies to pom.xml,
    and configures annotation processors for Lombok + MapStruct.
    """
    pom_path = os.path.join(project_path, "pom.xml")
    if not os.path.exists(pom_path):
        return

    # Register Maven namespace to avoid "ns0" prefixes
    ns = "http://maven.apache.org/POM/4.0.0"
    ET.register_namespace("", ns)
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ns_map = {"m": ns}

    # 1. Add Dependencies
    dependencies = root.find("m:dependencies", ns_map)
    if dependencies is None:
        dependencies = ET.SubElement(root, "{%s}dependencies" % ns)

    # JJWT & MapStruct versions
    jjwt_version = "0.12.5"
    mapstruct_version = "1.5.5.Final"
    lombok_version = "1.18.30"
    lombok_mapstruct_binding_version = "0.2.0"

    extra_deps = [
        ("io.jsonwebtoken", "jjwt-api", jjwt_version, None),
        ("io.jsonwebtoken", "jjwt-impl", jjwt_version, "runtime"),
        ("io.jsonwebtoken", "jjwt-jackson", jjwt_version, "runtime"),
        ("org.mapstruct", "mapstruct", mapstruct_version, None),
    ]

    # Helper to find if a dependency already exists
    def dep_exists(gid, aid):
        for dep in dependencies.findall("m:dependency", ns_map):
            g = dep.find("m:groupId", ns_map)
            a = dep.find("m:artifactId", ns_map)
            if g is not None and a is not None and g.text == gid and a.text == aid:
                return True
        return False

    for gid, aid, ver, scope in extra_deps:
        if not dep_exists(gid, aid):
            dep = ET.SubElement(dependencies, "{%s}dependency" % ns)
            ET.SubElement(dep, "{%s}groupId" % ns).text = gid
            ET.SubElement(dep, "{%s}artifactId" % ns).text = aid
            ET.SubElement(dep, "{%s}version" % ns).text = ver
            if scope:
                ET.SubElement(dep, "{%s}scope" % ns).text = scope

    # 2. Configure Annotation Processors
    processors = [
        ("org.projectlombok", "lombok", lombok_version),
        ("org.projectlombok", "lombok-mapstruct-binding", lombok_mapstruct_binding_version),
        ("org.mapstruct", "mapstruct-processor", mapstruct_version),
    ]

    def update_annotation_paths(parent_element):
        ap_paths = parent_element.find("m:annotationProcessorPaths", ns_map)
        if ap_paths is None:
            ap_paths = ET.SubElement(parent_element, "{%s}annotationProcessorPaths" % ns)

        for gid, aid, ver in processors:
            # Check if this processor already exists in this block
            exists = False
            for path in ap_paths.findall("m:path", ns_map):
                g = path.find("m:groupId", ns_map)
                a = path.find("m:artifactId", ns_map)
                if g is not None and a is not None and g.text == gid and a.text == aid:
                    # Update version if it exists
                    v = path.find("m:version", ns_map)
                    if v is not None:
                        v.text = ver
                    else:
                        ET.SubElement(path, "{%s}version" % ns).text = ver
                    exists = True
                    break

            if not exists:
                path = ET.SubElement(ap_paths, "{%s}path" % ns)
                ET.SubElement(path, "{%s}groupId" % ns).text = gid
                ET.SubElement(path, "{%s}artifactId" % ns).text = aid
                ET.SubElement(path, "{%s}version" % ns).text = ver

    # Find or create maven-compiler-plugin
    compiler_plugin = None
    for plugin in root.findall(".//m:plugin", ns_map):
        aid = plugin.find("m:artifactId", ns_map)
        if aid is not None and aid.text == "maven-compiler-plugin":
            compiler_plugin = plugin
            break

    if compiler_plugin is None:
        build = root.find("m:build", ns_map)
        if build is None:
            build = ET.SubElement(root, "{%s}build" % ns)
        plugins = build.find("m:plugins", ns_map)
        if plugins is None:
            plugins = ET.SubElement(build, "{%s}plugins" % ns)

        compiler_plugin = ET.SubElement(plugins, "{%s}plugin" % ns)
        ET.SubElement(compiler_plugin, "{%s}groupId" % ns).text = "org.apache.maven.plugins"
        ET.SubElement(compiler_plugin, "{%s}artifactId" % ns).text = "maven-compiler-plugin"
        ET.SubElement(compiler_plugin, "{%s}version" % ns).text = "3.11.0"

    # Update global configuration
    config = compiler_plugin.find("m:configuration", ns_map)
    if config is None:
        config = ET.SubElement(compiler_plugin, "{%s}configuration" % ns)
    update_annotation_paths(config)

    # Update configurations inside executions
    executions = compiler_plugin.find("m:executions", ns_map)
    if executions is not None:
        for execution in executions.findall("m:execution", ns_map):
            exec_config = execution.find("m:configuration", ns_map)
            if exec_config is not None:
                update_annotation_paths(exec_config)

    # Write back to file
    tree.write(pom_path, encoding="utf-8", xml_declaration=True)


def download_spring_boilerplate(project_name: str, db_type: str = "postgres"):
    """
    Downloads and extracts a Spring Boot project via the start.spring.io API.
    Automatically makes the Maven wrapper executable on Unix.
    """
    typer.secho(
        f"Generating Spring Boot backend '{project_name}' (Driver: {db_type})...",
        fg=typer.colors.CYAN,
    )

    # Java rule: a package name cannot contain hyphens
    safe_package_name = project_name.replace("-", "").replace("_", "").lower()

    # Dynamic mapping for the Spring API
    db_dependency = "postgresql" if db_type == "postgres" else "mysql"
    official_deps = [
        "web",
        "lombok",
        "data-jpa",
        "validation",
        "security",
        "devtools",
        "thymeleaf",
        db_dependency,  # postgresql or mysql
    ]
    dependencies = ",".join(official_deps)

    # Spring Initializr API parameters
    params = {
        "type": "maven-project",
        "language": "java",
        "baseDir": project_name,
        "groupId": "com.devctl",
        "artifactId": project_name,
        "name": project_name,
        "description": "Spring Boot project generated by devctl",
        "packageName": f"com.devctl.{safe_package_name}",
        "packaging": "jar",
        "javaVersion": "17",
        "dependencies": dependencies,
    }

    url = "https://start.spring.io/starter.zip"

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            typer.secho(f"Error: API Rejected: {response.text}", fg=typer.colors.RED)
            return False

        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(os.getcwd())

        project_path = os.path.join(os.getcwd(), project_name)

        # Patch the POM to add missing libraries (JJWT, MapStruct)
        patch_pom_xml(project_path)

        mvnw_path = os.path.join(project_path, "mvnw")
        if os.path.exists(mvnw_path):
            # Get current file permissions
            st = os.stat(mvnw_path)
            # Add execute permission (stat.S_IEXEC) for the current user
            os.chmod(mvnw_path, st.st_mode | stat.S_IEXEC)

        os.chdir(project_name)
        generate_spring_security()
        os.chdir("..")

        typer.secho(
            f"Backend successfully generated in folder ./{project_name}!",
            fg=typer.colors.GREEN,
        )
        return True

    except requests.exceptions.RequestException as e:
        typer.secho(f"Error: Network error contacting API: {e}", fg=typer.colors.RED)
        return False
