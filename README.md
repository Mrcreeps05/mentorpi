   # MentorPi Simulation
 
   **Course:** RAS 212, Introduction to ROS 2, Kansas State University Salina
   **Author:** JD Whitman
 
   ## Description
 
   A ROS 2 workspace for simulating the Hiwonder MentorPi M1 (Mecanum drive) in Gazebo. The robot model comes from Hiwonder's `mentorpi_description` package. My own `mentorpi_bringup` package holds the launch files, the ROS-Gazebo bridge configuration, and the xacro wrapper that adds the Gazebo plugins in simulation only.
 
   ## Tools
 
   - ROS 2 Jazzy
   - Gazebo Harmonic
   - MentorPi M1 (Mecanum), Raspberry Pi 5
 
   ## Layout
 
   - `mentorpi_description/`: Hiwonder's robot model (shared by simulation and the real robot)
   - `mentorpi_bringup/`: my launch files, bridge config, and xacro wrapper
 
   ## Goal
 
   Drive a simulated MentorPi with `teleop_twist_keyboard`, and use the same robot description on the real robot later in the course.