from __future__ import annotations

import io
import os
import platform
import threading
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Optional

import psutil
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Log,
    Select,
    TabbedContent,
    TabPane,
)

# Generator imports for Scaffolding Add
from devctl.commands.add import (
    generate_angular_resource,
    generate_django_resource,
    generate_fastapi_resource,
    generate_go_resource,
    generate_nest_resource,
    generate_nextjs_resource,
    generate_nodejs_resource,
    generate_react_resource,
    generate_spring_resource,
    generate_svelte_resource,
    generate_vue_resource,
)

# Boilerplate imports for Init
from devctl.commands.init import (
    download_spring_boilerplate,
    generate_angular_boilerplate,
    generate_django_boilerplate,
    generate_fastapi_boilerplate,
    generate_go_boilerplate,
    generate_nest_boilerplate,
    generate_nextjs_boilerplate,
    generate_nodejs_boilerplate,
    generate_react_boilerplate,
    generate_svelte_boilerplate,
    generate_vue_boilerplate,
)
from devctl.generators.docker_scaffold import discover_docker_projects, scaffold_docker_assets
from devctl.orchestrator.config_builder import generate_config
from devctl.orchestrator.process_manager import ProcessManager
from devctl.orchestrator.scanner import detect_environment


def make_bar(percent: float, width: int = 10) -> str:
    percent = max(0.0, min(100.0, percent))
    filled = int(percent / 100 * width)

    green_len = min(filled, int(0.50 * width))
    yellow_len = min(max(0, filled - green_len), int(0.25 * width))
    red_len = max(0, filled - green_len - yellow_len)
    dim_len = width - filled

    bar_str = (
        f"[green]{'|' * green_len}[/green]"
        f"[yellow]{'|' * yellow_len}[/yellow]"
        f"[red]{'|' * red_len}[/red]"
        f"[dim]{'.' * dim_len}[/dim]"
    )
    return f"[dim][[/dim]{bar_str}[dim]][/dim]"


class ServiceItem(ListItem):
    """Visual row representation of a service."""

    def __init__(self, service_name: str, manager: ProcessManager):
        super().__init__()
        self.service_name = service_name
        self.manager = manager
        self.classes = "service-item-row"

    def compose(self) -> ComposeResult:
        service = self.manager.services[self.service_name]
        yield Label(f"{service.name:<15}", id="name")
        yield Label(f"[{service.status}]", id="status", classes="status-label")
        yield Label("CPU: [dim][[/dim]..........[dim]][/dim] --%", id="cpu", classes="metric-label")
        yield Label(
            "RAM: [dim][[/dim]..........[dim]][/dim] --MB", id="ram", classes="metric-label"
        )

    def update_stats(self):
        service = self.manager.services[self.service_name]

        status_lbl = self.query_one("#status", Label)
        status_lbl.update(f"[{service.status}]")

        # Color mapping for status
        if service.status == "RUNNING":
            status_lbl.styles.color = "#00ff87"
        elif service.status in ("STOPPED", "CRASHED"):
            status_lbl.styles.color = "#ff4a4a"
        else:
            status_lbl.styles.color = "#ffb600"

        cpu_lbl = self.query_one("#cpu", Label)
        ram_lbl = self.query_one("#ram", Label)

        if service.status == "RUNNING":
            # Compact bar for CPU (width 10)
            cpu_bar = make_bar(service.cpu_percent, width=10)
            cpu_lbl.update(f"CPU: {cpu_bar} {service.cpu_percent:.1f}%")

            # RAM scale: assume max 1GB for local dev process bar calculation
            ram_percent = min(100.0, (service.memory_mb / 1024.0) * 100.0)
            ram_bar = make_bar(ram_percent, width=10)
            ram_lbl.update(f"RAM: {ram_bar} {service.memory_mb:.1f}MB")
        else:
            cpu_lbl.update("CPU: [..........] --%")
            ram_lbl.update("RAM: [..........] --MB")


class DevctlTUI(App):
    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("left", "prev_tab", "Prev Page"),
        ("right", "next_tab", "Next Page"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, single_panel: bool = False):
        super().__init__()
        self.single_panel = single_panel
        self.selected_service: Optional[str] = None
        self.perform_rescan()

    def perform_rescan(self) -> None:
        self.projects = discover_docker_projects(".")
        self.docker_composes = []
        for p in Path(".").rglob("docker-compose-db.yml"):
            if "node_modules" not in str(p) and "target" not in str(p) and ".git" not in str(p):
                self.docker_composes.append(p.parent)

        self.manager = ProcessManager(self.projects, self.docker_composes)
        self.env_state = detect_environment(".")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        if self.single_panel:
            with Vertical(id="single-container"):
                # Top row: System Monitor & Summary side-by-side
                with Horizontal(id="single-top-row"):
                    with Vertical(classes="dashboard-card", id="single-system-info"):
                        yield Label("[bold]SYSTEM MONITOR[/bold]", classes="section-title")
                        yield Label("CPU Usage: --", id="lbl-system-cpu")
                        yield Label("Memory (RAM): --", id="lbl-system-ram")
                        yield Label("Disk Storage: --", id="lbl-system-disk")
                        yield Label("Host System:  --", id="lbl-system-os")

                    with Vertical(classes="dashboard-card", id="single-db-summary"):
                        yield Label("[bold]PROJECT SUMMARY[/bold]", classes="section-title")
                        yield Label("[bold]Root:[/bold] " + self.env_state.get("project_root", "."))
                        yield Label(
                            f"[bold]Detected Projects:[/bold] {len(self.projects)}",
                            id="lbl-proj-count",
                        )
                        yield Label(
                            f"[bold]Detected DBs:[/bold] {len(self.docker_composes)}",
                            id="lbl-db-count",
                        )

                # Bottom row: Services List & Logs side-by-side
                with Horizontal(id="single-bottom-row"):
                    with Vertical(classes="services-list-panel", id="single-services-panel"):
                        yield Label("[bold]ACTIVE SERVICES[/bold]", classes="section-title")
                        with Horizontal(id="service-control-toolbar"):
                            yield Button("Start", id="btn-srv-start")
                            yield Button("Stop", id="btn-srv-stop")
                            yield Button("Restart", id="btn-srv-restart")
                        with Horizontal(id="service-control-bulk-toolbar"):
                            yield Button("Start All", id="btn-srv-startall")
                            yield Button("Stop All", id="btn-srv-stopall")
                        yield ListView(id="services-list")

                    with Vertical(classes="logs-panel", id="single-logs-panel"):
                        yield Label("[bold]SELECTED SERVICE LOGS[/bold]", classes="logs-title-bar")
                        yield Log(id="logs-view")
            yield Footer()
            return

        with Horizontal(id="top-nav-helper"):
            yield Label("◀", classes="nav-arrow")
            yield Label("Page: Dashboard (Use [← / →] to switch)", id="nav-hint-text")
            yield Label("▶", classes="nav-arrow")

        with TabbedContent(id="tui-tabs"):
            # Tab 1: Dashboard
            with TabPane("Dashboard", id="tab-dashboard"):
                with Vertical(classes="dashboard-container"):
                    yield Label("PROJECT DASHBOARD", classes="dashboard-title")

                    with Vertical(classes="dashboard-card", id="db-summary-card"):
                        yield Label(
                            "[bold]Repository Root:[/bold] "
                            + self.env_state.get("project_root", ".")
                        )
                        yield Label(
                            f"[bold]Detected Projects:[/bold] {len(self.projects)}",
                            id="lbl-proj-count",
                        )
                        yield Label(
                            "[bold]Detected Database Containers:[/bold] "
                            f"{len(self.docker_composes)}",
                            id="lbl-db-count",
                        )

                    yield Label("SYSTEM MONITOR", classes="dashboard-title")
                    with Vertical(classes="dashboard-card", id="system-info-card"):
                        yield Label("CPU Usage: --", id="lbl-system-cpu")
                        yield Label("Memory (RAM): --", id="lbl-system-ram")
                        yield Label("Disk Storage: --", id="lbl-system-disk")
                        yield Label("OS Platform: --", id="lbl-system-os")

                    yield Label("Framework Details", classes="dashboard-title")
                    yield Vertical(id="dashboard-frameworks-list")

            # Tab 2: Services Control
            with TabPane("Services Control", id="tab-services"):
                with Horizontal(classes="services-container"):
                    with Vertical(classes="services-list-panel"):
                        # Control buttons toolbar
                        yield Label(
                            "Service Controls", classes="dashboard-title", id="lbl-srv-controls"
                        )
                        with Horizontal(id="service-control-toolbar"):
                            yield Button("Start", id="btn-srv-start")
                            yield Button("Stop", id="btn-srv-stop")
                            yield Button("Restart", id="btn-srv-restart")
                        with Horizontal(id="service-control-bulk-toolbar"):
                            yield Button("Start All", id="btn-srv-startall")
                            yield Button("Stop All", id="btn-srv-stopall")

                        yield Label("Active Services", classes="dashboard-title")
                        yield ListView(id="services-list")

                    with Vertical(classes="logs-panel"):
                        yield Label("Selected Service Logs", classes="logs-title-bar")
                        yield Log(id="logs-view")

            # Tab 3: Docker Tools
            with TabPane("Docker Tools", id="tab-docker"):
                with Vertical(classes="form-container"):
                    yield Label("DOCKER SCAFFOLDING GENERATOR", classes="dashboard-title")

                    with Vertical(classes="form-group"):
                        yield Checkbox(
                            "Overwrite existing Dockerfiles (--force)",
                            id="docker-force",
                            classes="form-checkbox",
                        )
                        yield Checkbox(
                            "Dry Run (Simulate execution) (--dry-run)",
                            id="docker-dry-run",
                            classes="form-checkbox",
                        )

                    with Horizontal():
                        yield Button(
                            "Dockerize All Projects", id="btn-dockerize", classes="submit-button"
                        )
                        yield Button(
                            "Generate Deploy Compose", id="btn-deploy", classes="submit-button"
                        )

                    yield Label("Scaffolding Output Logs", classes="form-label")
                    yield Log(id="docker-output-log", classes="form-output-panel")

            # Tab 4: Add Resource Wizard
            with TabPane("Add Resource", id="tab-add"):
                with Vertical(classes="form-container"):
                    yield Label("SCAFFOLD NEW RESOURCE / ENTITY", classes="dashboard-title")

                    with Vertical(classes="form-group"):
                        yield Label("Resource Name (e.g. Product, Invoice)", classes="form-label")
                        yield Input(
                            placeholder="Resource Name",
                            id="add-resource-name",
                            classes="form-input",
                        )

                    with Vertical(classes="form-group"):
                        yield Label(
                            "Fields Definition (e.g. name:string, price:double)",
                            classes="form-label",
                        )
                        yield Input(
                            placeholder="name:type, age:int",
                            id="add-resource-fields",
                            classes="form-input",
                        )

                    with Vertical(classes="form-group"):
                        yield Label("Target Framework / Subproject", classes="form-label")
                        yield Select([], prompt="Choose target project", id="add-resource-target")

                    yield Button(
                        "Run Scaffolding Generator", id="btn-run-scaffold", classes="submit-button"
                    )

                    yield Label("Generator Output Logs", classes="form-label")
                    yield Log(id="add-output-log", classes="form-output-panel")

            # Tab 5: Init Project Wizard
            with TabPane("Init Project", id="tab-init"):
                with Vertical(classes="form-container"):
                    yield Label("BOOTSTRAP NEW PROJECT", classes="dashboard-title")

                    with Vertical(classes="form-group"):
                        yield Label("Project Name (e.g. catalog-service)", classes="form-label")
                        yield Input(
                            placeholder="Project Name", id="init-project-name", classes="form-input"
                        )

                    with Vertical(classes="form-group"):
                        yield Label("Boilerplate Framework", classes="form-label")
                        frameworks = [
                            ("Spring Boot", "spring"),
                            ("Angular", "angular"),
                            ("Vue.js", "vue"),
                            ("NestJS", "nest"),
                            ("NodeJS / Express", "nodejs"),
                            ("React", "react"),
                            ("Next.js", "nextjs"),
                            ("FastAPI", "fastapi"),
                            ("Django", "django"),
                            ("SvelteKit", "svelte"),
                            ("Go / Fiber", "go"),
                        ]
                        yield Select(
                            frameworks,
                            prompt="Choose target framework",
                            id="init-project-framework",
                        )

                    with Vertical(classes="form-group", id="spring-db-group"):
                        yield Label("Spring Database Engine (Spring-only)", classes="form-label")
                        db_engines = [
                            ("PostgreSQL", "postgres"),
                            ("MySQL", "mysql"),
                            ("MongoDB", "mongodb"),
                        ]
                        yield Select(
                            db_engines,
                            value="postgres",
                            prompt="Choose database",
                            id="init-project-db",
                        )

                    yield Button(
                        "Initialize Project Boilerplate", id="btn-run-init", classes="submit-button"
                    )

                    yield Label("Boilerplate Setup Output Logs", classes="form-label")
                    yield Log(id="init-output-log", classes="form-output-panel")

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_ui_elements()
        self.update_system_stats()
        self.set_interval(1.0, self.refresh_stats)
        self.set_interval(0.2, self.stream_new_logs)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        try:
            tab_names = {
                "tab-dashboard": "Dashboard",
                "tab-services": "Services Control",
                "tab-docker": "Docker Tools",
                "tab-add": "Add Resource",
                "tab-init": "Init Project",
            }
            active_id = event.pane.id if event.pane else event.tabbed_content.active
            name = tab_names.get(active_id, "Dashboard")
            self.query_one("#nav-hint-text", Label).update(
                f"Page: [bold]{name}[/bold] (Use [← / →] to switch)"
            )
        except Exception:
            pass

    def refresh_ui_elements(self) -> None:
        """Repopulates dynamic widgets from the scanned repository state."""
        # 1. Update counts on dashboard summary
        try:
            self.query_one("#lbl-proj-count", Label).update(
                f"[bold]Detected Projects:[/bold] {len(self.projects)}"
            )
            self.query_one("#lbl-db-count", Label).update(
                f"[bold]Detected Database Containers:[/bold] {len(self.docker_composes)}"
            )
        except Exception:
            pass

        # 2. Update dashboard list (tabbed mode only)
        if not self.single_panel:
            try:
                list_container = self.query_one("#dashboard-frameworks-list", Vertical)
                list_container.remove_children()
                if not self.projects:
                    list_container.mount(
                        Label(
                            "[yellow]No local projects found. "
                            "Use the 'Init Project' tab to bootstrap one.[/yellow]"
                        )
                    )
                else:
                    for p in self.projects:
                        labels = [
                            Label(f"[bold]{p.name}[/bold] ({p.kind.upper()})"),
                            Label(f"  Path: {p.path}"),
                        ]
                        if p.node_version:
                            labels.append(Label(f"  Node Version: {p.node_version}"))
                        if p.java_version:
                            labels.append(Label(f"  Java Version: {p.java_version}"))
                        labels.append(Label(f"  Service context: {p.relative_context}"))

                        item_v = Vertical(*labels, classes="framework-item")
                        list_container.mount(item_v)
            except Exception:
                pass

        # 3. Update Services Control tab
        try:
            lv = self.query_one("#services-list", ListView)
            lv.clear()
            for name in self.manager.services.keys():
                lv.append(ServiceItem(name, self.manager))
        except Exception:
            pass

        # Reset selection if invalid
        if self.selected_service not in self.manager.services:
            self.selected_service = None

        # 4. Update Target Project Select dropdown in Add tab (tabbed mode only)
        if not self.single_panel:
            try:
                select_add = self.query_one("#add-resource-target", Select)
                options = [(f"{p.name} ({p.kind})", p.name) for p in self.projects]
                select_add.options = options
            except Exception:
                pass

    def refresh_stats(self) -> None:
        self.manager.update_metrics()
        for item in self.query(ServiceItem):
            item.update_stats()
        self.update_system_stats()

    def update_system_stats(self) -> None:
        # CPU
        cpu = psutil.cpu_percent(interval=None)
        cpu_bar = make_bar(cpu, width=20)
        try:
            self.query_one("#lbl-system-cpu", Label).update(f"CPU Usage:    {cpu_bar} {cpu:.1f}%")
        except Exception:
            pass

        # RAM
        ram = psutil.virtual_memory()
        total_ram = ram.total / (1024**3)
        used_ram = ram.used / (1024**3)
        ram_bar = make_bar(ram.percent, width=20)
        try:
            self.query_one("#lbl-system-ram", Label).update(
                f"Memory (RAM): {ram_bar} {used_ram:.1f} GB / {total_ram:.1f} GB ({ram.percent}%)"
            )
        except Exception:
            pass

        # Disk
        try:
            disk = psutil.disk_usage(".")
            total_disk = disk.total / (1024**3)
            used_disk = disk.used / (1024**3)
            disk_bar = make_bar(disk.percent, width=20)
            self.query_one("#lbl-system-disk", Label).update(
                f"Disk Storage: {disk_bar} {used_disk:.1f} GB / "
                f"{total_disk:.1f} GB ({disk.percent}%)"
            )
        except Exception:
            pass

        # OS Platform
        try:
            import socket

            hostname = socket.gethostname()
            self.query_one("#lbl-system-os", Label).update(
                f"Host System:  [bold]{hostname}[/bold] | "
                f"{platform.system()} {platform.release()} ({platform.machine()})"
            )
        except Exception:
            pass

    def stream_new_logs(self) -> None:
        if not self.selected_service:
            return
        service = self.manager.services[self.selected_service]
        log_view = self.query_one("#logs-view", Log)

        with service.log_lock:
            while service.logs:
                line = service.logs.pop(0)
                log_view.write_line(line)

    def _get_target_service(self) -> str | None:
        if self.selected_service and self.selected_service in self.manager.services:
            return self.selected_service
        try:
            lv = self.query_one("#services-list", ListView)
            if lv.highlighted_child and isinstance(lv.highlighted_child, ServiceItem):
                return lv.highlighted_child.service_name
        except Exception:
            pass
        if self.manager.services:
            return next(iter(self.manager.services.keys()))
        return None

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and isinstance(event.item, ServiceItem):
            self.selected_service = event.item.service_name
            log_view = self.query_one("#logs-view", Log)
            log_view.clear()
            log_view.write_line(f"--- Viewing logs for {self.selected_service} ---")

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and isinstance(event.item, ServiceItem):
            self.selected_service = event.item.service_name

    def action_start_selected(self) -> None:
        target = self._get_target_service()
        if target:
            self.manager.start_service(target)

    def action_stop_selected(self) -> None:
        target = self._get_target_service()
        if target:
            self.manager.stop_service(target)

    def action_restart_selected(self) -> None:
        target = self._get_target_service()
        if target:
            self.manager.restart_service(target)

    def action_start_all(self) -> None:
        for name in self.manager.services.keys():
            self.manager.start_service(name)

    def action_stop_all(self) -> None:
        for name in self.manager.services.keys():
            self.manager.stop_service(name)

    def action_prev_tab(self) -> None:
        if self.single_panel:
            return
        tabs = self.query_one("#tui-tabs", TabbedContent)
        tab_ids = ["tab-dashboard", "tab-services", "tab-docker", "tab-add", "tab-init"]
        try:
            current_index = tab_ids.index(tabs.active)
            prev_index = (current_index - 1) % len(tab_ids)
            tabs.active = tab_ids[prev_index]
        except Exception:
            pass

    def action_next_tab(self) -> None:
        if self.single_panel:
            return
        tabs = self.query_one("#tui-tabs", TabbedContent)
        tab_ids = ["tab-dashboard", "tab-services", "tab-docker", "tab-add", "tab-init"]
        try:
            current_index = tab_ids.index(tabs.active)
            next_index = (current_index + 1) % len(tab_ids)
            tabs.active = tab_ids[next_index]
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        # Runner toolbar triggers
        if button_id == "btn-srv-start":
            self.action_start_selected()
        elif button_id == "btn-srv-stop":
            self.action_stop_selected()
        elif button_id == "btn-srv-restart":
            self.action_restart_selected()
        elif button_id == "btn-srv-startall":
            self.action_start_all()
        elif button_id == "btn-srv-stopall":
            self.action_stop_all()

        # Docker triggers
        elif button_id == "btn-dockerize":
            force = self.query_one("#docker-force", Checkbox).value
            dry_run = self.query_one("#docker-dry-run", Checkbox).value
            threading.Thread(target=self.run_dockerize, args=(force, dry_run), daemon=True).start()
        elif button_id == "btn-deploy":
            force = self.query_one("#docker-force", Checkbox).value
            threading.Thread(target=self.run_deploy, args=(force,), daemon=True).start()

        # Scaffolder Add triggers
        elif button_id == "btn-run-scaffold":
            name = self.query_one("#add-resource-name", Input).value
            fields = self.query_one("#add-resource-fields", Input).value
            target_proj_name = self.query_one("#add-resource-target", Select).value

            if not name:
                self.query_one("#add-output-log", Log).write_line(
                    "Error: Resource Name is required."
                )
                return
            if not target_proj_name or target_proj_name == Select.BLANK:
                self.query_one("#add-output-log", Log).write_line(
                    "Error: Target project must be selected."
                )
                return

            target_proj = next((p for p in self.projects if p.name == target_proj_name), None)
            if not target_proj:
                self.query_one("#add-output-log", Log).write_line(
                    f"Error: Target project '{target_proj_name}' not found."
                )
                return

            threading.Thread(
                target=self.run_scaffolding, args=(name, fields, target_proj), daemon=True
            ).start()

        # Boilerplate Init triggers
        elif button_id == "btn-run-init":
            name = self.query_one("#init-project-name", Input).value
            framework = self.query_one("#init-project-framework", Select).value
            db = self.query_one("#init-project-db", Select).value

            if not name:
                self.query_one("#init-output-log", Log).write_line(
                    "Error: Project Name is required."
                )
                return
            if not framework or framework == Select.BLANK:
                self.query_one("#init-output-log", Log).write_line(
                    "Error: Boilerplate framework must be selected."
                )
                return

            threading.Thread(
                target=self.run_init_project, args=(name, framework, db), daemon=True
            ).start()

    def run_dockerize(self, force: bool, dry_run: bool) -> None:
        log = self.query_one("#docker-output-log", Log)
        log.clear()
        log.write_line("Starting Docker scaffolding...\n")

        f = io.StringIO()
        try:
            with redirect_stdout(f), redirect_stderr(f):
                result = scaffold_docker_assets(".", force=force, dry_run=dry_run)
                print(f"Scaffolding complete for {result.root_path}")
                print(f"Discovered: {len(result.services)} services.")
                for op in result.operations:
                    print(f"  - {op.action}: {op.path.name}")
        except Exception as e:
            print(f"Error during Dockerize: {e}", file=f)

        for line in f.getvalue().splitlines():
            log.write_line(line)
        self.trigger_rescan_and_refresh()

    def run_deploy(self, force: bool) -> None:
        log = self.query_one("#docker-output-log", Log)
        log.clear()
        log.write_line("Generating production docker-compose...\n")

        f = io.StringIO()
        try:
            with redirect_stdout(f), redirect_stderr(f):
                result = scaffold_docker_assets(".", force=force, dry_run=False)
                print("Production compose deployment scaffolding complete.")
                for op in result.operations:
                    if "docker-compose-prod.yml" in str(op.path):
                        print(f"  - {op.action}: {op.path.name}")
        except Exception as e:
            print(f"Error during Deploy generation: {e}", file=f)

        for line in f.getvalue().splitlines():
            log.write_line(line)

    def run_scaffolding(self, name: str, fields: str, project) -> None:
        log = self.query_one("#add-output-log", Log)
        log.clear()
        log.write_line(
            f"Running resource generator for '{name}' on project "
            f"'{project.name}' ({project.kind})...\n"
        )

        f = io.StringIO()
        original_dir = Path.cwd()
        try:
            with redirect_stdout(f), redirect_stderr(f):
                os.chdir(str(project.path))
                if project.kind == "spring":
                    generate_spring_resource(name, fields)
                elif project.kind == "angular":
                    generate_angular_resource(name, fields, root_path=".")
                elif project.kind == "vue":
                    generate_vue_resource(name, fields, root_path=".")
                elif project.kind == "nest":
                    generate_nest_resource(name, fields, root_path=".")
                elif project.kind == "react":
                    generate_react_resource(name, fields, root_path=".")
                elif project.kind == "nextjs":
                    generate_nextjs_resource(name, fields, root_path=".")
                elif project.kind == "fastapi":
                    generate_fastapi_resource(name, fields, root_path=".")
                elif project.kind == "django":
                    generate_django_resource(name, fields, root_path=".")
                elif project.kind == "svelte":
                    generate_svelte_resource(name, fields, root_path=".")
                elif project.kind == "go":
                    generate_go_resource(name, fields, root_path=".")
                elif project.kind == "nodejs":
                    generate_nodejs_resource(name, fields, root_path=".")
                else:
                    print(f"Error: Unknown framework kind {project.kind}")
                print("\nGeneration finished successfully!")
        except Exception as e:
            print(f"Error during scaffolding: {e}", file=f)
        finally:
            os.chdir(original_dir)

        for line in f.getvalue().splitlines():
            log.write_line(line)

    def run_init_project(self, name: str, framework: str, db: str) -> None:
        log = self.query_one("#init-output-log", Log)
        log.clear()
        log.write_line(f"Bootstrapping new project '{name}' with framework '{framework}'...\n")

        f = io.StringIO()
        try:
            with redirect_stdout(f), redirect_stderr(f):
                if framework == "spring":
                    download_spring_boilerplate(name, db_type=db)
                    generate_config(name, db_type=db, custom_port=None)
                elif framework == "angular":
                    generate_angular_boilerplate(name)
                elif framework == "vue":
                    generate_vue_boilerplate(name)
                elif framework == "nest":
                    generate_nest_boilerplate(name)
                elif framework == "nodejs":
                    generate_nodejs_boilerplate(name)
                elif framework == "react":
                    generate_react_boilerplate(name)
                elif framework == "nextjs":
                    generate_nextjs_boilerplate(name)
                elif framework == "fastapi":
                    generate_fastapi_boilerplate(name)
                elif framework == "django":
                    generate_django_boilerplate(name)
                elif framework == "svelte":
                    generate_svelte_boilerplate(name)
                elif framework == "go":
                    generate_go_boilerplate(name)
                else:
                    print(f"Error: Unknown framework boilerplate '{framework}'")
                print("\nProject initialized successfully!")
        except Exception as e:
            print(f"Error during initialization: {e}", file=f)

        for line in f.getvalue().splitlines():
            log.write_line(line)

        # Trigger directory rescan and refresh widgets
        self.trigger_rescan_and_refresh()

    def trigger_rescan_and_refresh(self) -> None:
        """Helper to safely perform rescan and trigger UI updates."""
        self.perform_rescan()
        self.refresh_ui_elements()

    def on_unmount(self) -> None:
        self.manager.cleanup_all()


if __name__ == "__main__":
    app = DevctlTUI()
    app.run()
