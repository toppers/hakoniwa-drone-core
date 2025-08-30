English | [日本語](overview.md)

# 📘 What is this?
This document explains how the "Hakoniwa Drone Simulator" is designed and how it can be integrated with other systems.
It will be explained in three representative patterns, from simple standalone use to complex configurations utilizing shared memory communication and containers.

# Hakoniwa Drone Simulator Overall Architecture

The Hakoniwa Drone Simulator is a flexible drone simulator that operates as a "Hakoniwa Asset" on top of the Hakoniwa core functions.
This simulator functions as a "Hakoniwa Asset (execution unit)" within the entire Hakoniwa system, providing the physical and control models of the drone.

---

## Hakoniwa Architecture

Now, what is Hakoniwa?

It is a "simulation hub" for integrating multiple simulators and systems and operating them on a unified timeline.
At its core are the "Hakoniwa core functions," which can be described as a real-time OS for simulators.

Hakoniwa is composed of the following five main elements, each supporting its function as a hub:

![image](/docs/images/architecture-hakoniwa.png)

---

### 🟨 Hakoniwa Asset

By registering existing simulators and control programs as "Hakoniwa Assets" and connecting them via the Hakoniwa API, unified communication and interoperability become possible even between modules of different environments and implementations.

**Use Case Examples:**

*   Simultaneous execution of physical simulation by Gazebo and visual representation by Unity.
*   Integration of ROS-based control nodes and C#-based XR applications.
*   Integrated use of Hakoniwa Drone Simulator with Unity, MAVLink, and XR.

---

### 🔌 Hakoniwa API

A core interface designed with multi-language support (Python, C/C++, C#, Rust, Elixir, etc.) in mind.
This allows for flexible asset development and integration while leveraging existing assets.

---

### ⏱ Hakoniwa Time Synchronization

To establish a consistent simulation in a distributed environment, time synchronization between assets is essential.
Hakoniwa introduces a unique time synchronization mechanism that considers the maximum allowable delay, achieving both real-time performance and reproducibility while enabling parallel execution of multiple assets.

---

### 📨 Hakoniwa PDU Data

Communication data between assets is standardized in the "PDU (Protocol Data Unit)" format.
It is a mechanism where data structures defined in ROS IDL (Interface Definition Language) are automatically type-converted and serialized/deserialized.

Examples of supported protocols:

*   ROS 2 / DDS
*   Zenoh
*   MQTT
*   UDP
*   Shared Memory (MMAP)

---

### 🟩 Hakoniwa Components

Main components include:

*   **Hakoniwa Conductor**: Manages the overall simulation environment control, time synchronization, and load balancing.
*   **Hakoniwa Bridge**: Acts as a relay connecting the virtual and real spaces, supporting real-time communication.

---

## Hakoniwa Drone Simulator Architecture

The Hakoniwa Drone Simulator, as a Hakoniwa asset, provides the physical and control models for a drone.
It can be integrated with other simulators and systems to realize realistic drone simulations.

First, the minimum configuration architecture is as follows:

![image](/docs/images/architecture-hakoniwa-drone.png)

The Hakoniwa Drone Simulator is composed of the following two main layers:

*   **Service**
    A layer that provides the drone's physical and control models (can be executed standalone, independent of Hakoniwa).

*   **Hakoniwa**
    A layer that exposes the functions of the Service layer to the outside and communicates with the Hakoniwa core.

This configuration allows for flexible composition and extension according to the application. Three representative architecture examples are introduced below.


---

### Without Hakoniwa: Single Pattern

![image](/docs/images/architecture-service.png)

This is a configuration where the Hakoniwa Drone Simulator is used standalone as a C library.
It operates only with the Service layer, without communicating with the Hakoniwa core.

Example of invocation methods:

*   **Unreal Engine**: Direct call from C++.
*   **Unity**: Call from C# via P/Invoke.
*   **Java (JME)**: Integration with JNI.
*   **Python**: Can be embedded as a C extension module.

---

### With Hakoniwa: Shared Memory Pattern

![image](/docs/images/architecture-hakoniwa-drone-1.png)

A configuration that connects to the Hakoniwa core via shared memory (MMAP).
It enables low-latency communication and realizes simulations with high real-time performance.

Integration examples:

*   Real-time visualization with Unity/Unreal Engine.
*   Integration with assets that simulate environmental changes (wind, temperature, etc.).
*   Control from Python scripts.
*   Configuration with separated visualization and control.

---

### With Hakoniwa: Container Pattern

![image](/docs/images/architecture-hakoniwa-drone-2.png)

A configuration where Hakoniwa and the Hakoniwa Drone Simulator are executed together on Docker containers.
It absorbs environmental differences and allows for flexible deployment.

**Note:**

*   GUI applications (like Unity or Unreal Engine) do not run inside containers, so they need to be run on the native host and integrated via a **Hakoniwa Bridge**.
*   For example, a configuration utilizing `hakoniwa-webserver` as a relay is effective.


---

## Further Extension

The architectures described here are just a few examples, and other configurations are possible. For example, a digital twin configuration that integrates with real-world robot systems can also be realized.

The Hakoniwa Bridge function plays a major role in achieving this.

![image](/docs/images/architecture-bridge.png)

- [AR Bridge](https://github.com/toppers/hakoniwa-ar-bridge):
  Connects AR devices (like HoloLens) with Hakoniwa to provide real-time AR experiences.
- [Web Server](https://github.com/toppers/hakoniwa-webserver):
   A WebSocket server that enables bidirectional communication between clients and Hakoniwa.
- [ROS Bridge](https://github.com/toppers/hakoniwa-bridge):
  Connects ROS nodes with Hakoniwa via Zenoh/ROS2 communication, realizing integration with the ROS ecosystem.
- [MAVLINK Bridge](https://github.com/toppers/hakoniwa-drone-core/tree/main/mavlink/bridge):
  Connects GCS such as Mission Planner with Hakoniwa using the MAVLink protocol.
- MCP Server:
  Realizes data exchange between Hakoniwa and AI agents using the Model Context Protocol (MCP).
