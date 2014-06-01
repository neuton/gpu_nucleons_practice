GPU nucleons practice
======================
This is a simple python (with python-ogre) + C + OpenCL toy implementation of simulation of interacting nucleons.

Requirements
--------------
- Windows
- OpenCL SDK
- gcc
- make
- python (2.*)
- python-ogre (download OGRE, OIS and "plugins" and place them into the root directory:
https://www.dropbox.com/sh/4i852xb5w9i2dtr/AACE6H5EkiKNDD0jkYht77UGa (for Windows))

How to run
--------------
just run "main.py" (choose graphics options; when loaded, press [Enter] to start/stop simulation, use mouse/[+]/[-] to change point of view);
"make" is executed by script, so it's not necessary to run it manually.

Short description
--------------
Computation of particles positions is implemented in OpenCL C, C is used for OpenCL runtime calls.
Visualization is made with the help of python wrapper for OGRE graphics engine (http://www.ogre3d.org/ http://wiki.python-ogre.org/index.php?title=Main_Page).
Python is used as a quick and handy wrapper to clue it all together.

Key source files:
- main.py -- the main python script which should be executed
- host.c -- source for C library which is used from python, includes OpenCL initialization, kernel launch functions etc.
- kernel.cl -- source for OpenCL C kernel where main computations are
- test.c -- execution time testing source
- Makefile -- build setup file, you probably won't need to edit it
- builddef.txt -- definitions included in Makefile, you may need to edit it

Other files:
- simulation.py -- classes which setup the scene, run OpenCL kernels etc.
- scene.py -- some base scene classes for inheritance used in simulation.py
- framework.py -- simple framework for python-ogre (python wrapper of 3D graphics engine) usage
- opencl.c/h -- simple wrapper for OpenCL functions/types
- cl_error.c/h -- helper functions for OpenCL usage
- ogre.cfg/resources.cfg/plugins.cfg.*/ -- OGRE config files
- resources/* -- material/texture used
- .git -- folder used by git (http://git-scm.com/)
- .gitignore -- little "config" for git
- README.md -- file containing this text

Tasks
--------------
- download and successfully run (don't forget to meet requirements)
- tune strong interaction (potential) so that simulation would look at least slightly plausible
- write your own fast, clear and simple visualization code (OGRE is an overkill for this purpose, I'd recommend using OpenGL-OpenCL interoperability through shared context and VBO); note that this is a heavy task though
- maybe create some user interface (UI), for example with QT (PyQT or whatever)
- experiment more with particles interactions; any ideas and improvements concerning algorithm/model/potentials etc. are welcome; maybe try to implement "solid spheres" collisions
- play/modify/improve/do whatever you'd like, make some cool things

Contacts
--------------
in case something goes wrong and/or you have questions, please, contact me
- by mail: mr.neuton@gmail.com
- by skype: neuton666
- by vkontaktique: vk.com/id15239112
