- tags: [java](/tags.md#java)
- date: 2013-12-08

# Three-Tier Design In OO Development

The three tier include graphical user interface (GUI) classes, problem domain classes, and data access classes.

The UML diagrams discussed are used in both OO analysis and OO design. This is different from the structured approach where structured amalysis use DFDs and ERDs, and structured design uses structure charts. This is one of the benefits of OO development--the same modeling constructs are used throughout the system development life cycle.

A useful way to look at the distinction between OOA and OOD is based on the *three-ties design* approach.The three ties include graphical user interface (GUI) classes, problem domain classes, and data access classes. Three ties design requires thar OO system developers separate three categories of classes when designing and building the system. First, you will indentify and specify the proble domain classes, the classes of objects that involve the user to interact with the problem domain classes. Finally, you specify data access classes thar allow problem domain classess to interact with the database. Once all three ties are complete, they are ready to work together as a complete system.

The user interacts with a graphical user interface usually made up of windows that contain GUI objects such as menus, buttons, text boxes, and labels. The user clicks a mouse and presses keys to get the system to respond. The user does no directly interact with problem domain objects; rather, the GUI objects interact with problem domain objects based on the action of the user. By separating the user interface classes from the problem domain classes, you are able to focus on the problem domain classes independent of the user interface.