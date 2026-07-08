"""
Azure Architecture Diagram Generator for the Contoso order processing platform.
Generates PNG, DOT, and Draw.io output files.
"""

import subprocess
from pathlib import Path

from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.compute import AppServices, FunctionApps
from diagrams.azure.database import SQLServers, SQLDatabases
from diagrams.azure.devops import ApplicationInsights
from diagrams.azure.integration import ServiceBus
from diagrams.azure.network import (
    ApplicationGateway,
    Firewall,
    FrontDoors,
    NetworkSecurityGroupsClassic,
    PrivateEndpoint,
    RouteTables,
    Subnets,
    VirtualNetworks,
)
from diagrams.azure.security import KeyVaults
from diagrams.azure.storage import StorageAccounts
from diagrams.onprem.client import Users

base_dir = Path(__file__).resolve().parent
output_path = base_dir / "diagrams" / "contoso_architecture"
output_path.parent.mkdir(parents=True, exist_ok=True)


def _write_fallback_outputs(base_path: Path) -> None:
    dot_path = base_path.with_suffix(".dot")
    drawio_path = base_path.with_suffix(".drawio")

    dot_content = '''digraph "Contoso Order Processing Architecture" {
  graph [label="Contoso Order Processing Architecture", labelloc=t, splines=ortho, rankdir=TB];
  node [shape=box, style=rounded];
  users [label="Users"];
  afd [label="Azure Front Door"];
  agw [label="Application Gateway\n(WAF)"];
  webapp [label="Web App"];
  backend_api [label="Backend API"];
  func_app [label="Function App"];
  service_bus [label="Service Bus"];
  sql_db [label="SQL Database"];
  storage [label="Storage Account"];
  keyvault [label="Key Vault"];
  azfw [label="Azure Firewall"];
  law [label="Log Analytics"];
  appi [label="Application Insights"];

  users -> afd;
  afd -> agw;
  agw -> webapp;
  webapp -> backend_api;
  backend_api -> sql_db;
  backend_api -> storage;
  func_app -> service_bus;
  service_bus -> func_app;
  func_app -> sql_db;
  webapp -> keyvault;
  backend_api -> keyvault;
  func_app -> keyvault;
  webapp -> azfw;
  backend_api -> azfw;
  func_app -> azfw;
  webapp -> law;
  backend_api -> law;
  func_app -> law;
  sql_db -> law;
  storage -> law;
  webapp -> appi;
  backend_api -> appi;
  func_app -> appi;
}
'''
    dot_path.write_text(dot_content, encoding="utf-8")

    drawio_content = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2026-07-08T00:00:00.000Z" agent="Copilot" version="24.7.17">
  <diagram name="Contoso Order Processing Architecture" id="contoso-architecture">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Contoso Order Processing Architecture" style="rounded=1;whiteSpace=wrap;html=1;fontSize=20;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="420" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="Users&#xa;Azure Front Door&#xa;Application Gateway&#xa;Web App&#xa;Backend API&#xa;Function App&#xa;Service Bus&#xa;SQL Database&#xa;Storage Account&#xa;Key Vault&#xa;Azure Firewall&#xa;Log Analytics&#xa;Application Insights" style="rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=top;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="40" y="130" width="320" height="240" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
'''
    drawio_path.write_text(drawio_content, encoding="utf-8")


# Graph attributes for clean layout
graph_attr = {
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.2",
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5",
    "compound": "true",
}

vnet_cluster_attr = {
    "fontsize": "14",
    "bgcolor": "#E8F4F8",
    "style": "dashed",
    "margin": "25",
}

frontend_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#E3F2FD",
    "style": "rounded",
    "margin": "15",
}

backend_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#F3E5F5",
    "style": "rounded",
    "margin": "15",
}

data_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#FFF3E0",
    "style": "rounded",
    "margin": "15",
}

firewall_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#FFEBEE",
    "style": "rounded",
    "margin": "15",
}

monitoring_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#E8F5E9",
    "style": "rounded",
    "margin": "15",
}

try:
    with Diagram(
        "Contoso Order Processing Architecture",
        filename=str(output_path),
        outformat=["png", "dot"],
        show=False,
        direction="TB",
        graph_attr=graph_attr,
    ):
        users = Users("Users")
        afd = FrontDoors("afd-contoso\n(Azure Front Door)")

        with Cluster("vnet-contoso-auea-001\n(10.10.0.0/16)", graph_attr=vnet_cluster_attr):
            vnet_icon = VirtualNetworks("VNet")

            with Cluster("snet-frontend\n(10.10.1.0/24)", graph_attr=frontend_cluster_attr):
                subnet_frontend = Subnets("snet-frontend")
                nsg_frontend = NetworkSecurityGroupsClassic("NSG-Frontend")
                agw = ApplicationGateway("agw-contoso\n(WAF)")
                app_plan_web = AppServices("asp-contoso-prod\n(App Service Plan)")
                webapp = AppServices("app-frontend-portal\n(Web App)")

            with Cluster("snet-backend\n(10.10.2.0/24)", graph_attr=backend_cluster_attr):
                subnet_backend = Subnets("snet-backend")
                nsg_backend = NetworkSecurityGroupsClassic("NSG-Backend")
                app_plan_backend = AppServices("asp-contoso-backend\n(Internal App Service Plan)")
                backend_api = AppServices("app-order-api\n(Backend API)")
                func_app = FunctionApps("func-order-processor\n(Function App)")
                service_bus = ServiceBus("sb-contoso-orders\n(Service Bus)")

            with Cluster("snet-data\n(10.10.3.0/24)", graph_attr=data_cluster_attr):
                subnet_data = Subnets("snet-data")
                nsg_data = NetworkSecurityGroupsClassic("NSG-Data")
                sql_server = SQLServers("sqlsrv-contoso")
                sql_db = SQLDatabases("sqldb-orders")
                storage = StorageAccounts("stcontosodata001")
                keyvault = KeyVaults("kv-contoso-prod")
                sql_pe = PrivateEndpoint("SQL Private Endpoint")
                storage_pe = PrivateEndpoint("Storage Private Endpoint")
                kv_pe = PrivateEndpoint("Key Vault Private Endpoint")

            with Cluster("Firewall & Routing", graph_attr=firewall_cluster_attr):
                azfw = Firewall("azfw-contoso\n(Azure Firewall)")
                route_table = RouteTables("Route Table\n(Default route to Firewall)")

            with Cluster("Monitoring", graph_attr=monitoring_cluster_attr):
                law = LogAnalyticsWorkspaces("law-contoso-prod\n(Log Analytics)")
                appi = ApplicationInsights("appi-contoso\n(Application Insights)")

        users >> Edge(label="HTTPS") >> afd
        afd >> Edge(label="HTTPS") >> agw
        agw >> Edge(label="HTTPS") >> webapp

        webapp >> Edge(label="API") >> backend_api

        backend_api >> Edge(label="SQL\n(Private)") >> sql_db
        backend_api >> Edge(label="Storage\n(Private)") >> storage

        func_app >> Edge(label="Messages") >> service_bus
        service_bus >> Edge(label="Process") >> func_app
        func_app >> Edge(label="SQL\n(Private)") >> sql_db

        webapp >> Edge(label="Secrets", style="dotted") >> keyvault
        backend_api >> Edge(label="Secrets", style="dotted") >> keyvault
        func_app >> Edge(label="Secrets", style="dotted") >> keyvault

        sql_server >> Edge(label="hosts") >> sql_db
        sql_pe >> Edge(label="Private Link") >> sql_server
        storage_pe >> Edge(label="Private Link") >> storage
        kv_pe >> Edge(label="Private Link") >> keyvault

        route_table >> Edge(label="default route") >> azfw
        webapp >> Edge(label="Outbound", style="dashed") >> azfw
        backend_api >> Edge(label="Outbound", style="dashed") >> azfw
        func_app >> Edge(label="Outbound", style="dashed") >> azfw

        webapp >> Edge(label="Logs", style="dotted", color="green") >> law
        backend_api >> Edge(label="Logs", style="dotted", color="green") >> law
        func_app >> Edge(label="Logs", style="dotted", color="green") >> law
        sql_db >> Edge(label="Logs", style="dotted", color="green") >> law
        storage >> Edge(label="Logs", style="dotted", color="green") >> law

        webapp >> Edge(label="Telemetry", style="dotted", color="green") >> appi
        backend_api >> Edge(label="Telemetry", style="dotted", color="green") >> appi
        func_app >> Edge(label="Telemetry", style="dotted", color="green") >> appi

    print("✓ PNG and DOT output written to diagrams/")
except Exception as exc:
    print(f"⚠ Diagram generation failed: {exc}")
    print("Generating fallback DOT and Draw.io files instead.")
    _write_fallback_outputs(output_path)

if not output_path.with_suffix(".dot").exists():
    _write_fallback_outputs(output_path)

try:
    subprocess.run(
        [
            "graphviz2drawio",
            str(output_path.with_suffix(".dot")),
            "-o",
            str(output_path.with_suffix(".drawio")),
        ],
        check=True,
        capture_output=True,
    )
    print(f"✓ Draw.io file generated: {output_path.with_suffix('.drawio')}")
except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
    print(f"⚠ Draw.io conversion unavailable, using fallback output: {exc}")
    if not output_path.with_suffix(".drawio").exists():
        _write_fallback_outputs(output_path)

print("\nGenerated files:")
print(f"  - {output_path.with_suffix('.png')}")
print(f"  - {output_path.with_suffix('.dot')}")
print(f"  - {output_path.with_suffix('.drawio')}")
