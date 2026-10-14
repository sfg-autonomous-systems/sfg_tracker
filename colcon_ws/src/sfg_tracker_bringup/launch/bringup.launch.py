import sfg_utils.launch_utils
from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.substitutions import FindPackageShare
from rospkg import get_package_name
from sfg_utils.fqn import RosFqnBuilder, RosFqnSegment, Scope

package_name = get_package_name(__file__)
local_namespace = RosFqnBuilder().scope(Scope.Local).agent()
global_namespace = RosFqnBuilder().scope(Scope.Global).agent()


def generate_launch_description() -> LaunchDescription:
    agent_launch_description_entities = (
        sfg_utils.launch_utils.get_launch_description_entities(
            "sfg_agent", "agent.launch.py"
        )
    )

    vicon_bridge_node = ComposableNode(
        package="sfg_vicon_bridge",
        plugin="sfg_vicon_bridge::ViconBridge",
        namespace=local_namespace.build(RosFqnSegment.Scope, RosFqnSegment.Agent),
        name="vicon_bridge",
        parameters=[
            PathJoinSubstitution(
                [
                    FindPackageShare(package_name),
                    "config",
                    "vicon_bridge.yaml",
                ]
            ),
        ],
        extra_arguments=[{"use_intra_process_comms": True}],
    )

    return LaunchDescription(
        [
            *agent_launch_description_entities.launch_arguments,
            *agent_launch_description_entities.nodes,
            ComposableNodeContainer(
                package="rclcpp_components",
                executable="component_container_mt",
                namespace=local_namespace.build(
                    RosFqnSegment.Scope, RosFqnSegment.Agent
                ),
                name="bringup_container",
                composable_node_descriptions=[
                    *agent_launch_description_entities.composable_nodes,
                    vicon_bridge_node,
                ],
                output="screen",
            ),
        ]
    )
