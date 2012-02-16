Installation
============

Hardware Prerequisites
----------------------

none

Software Prerequisites
----------------------

Gnomon depends on several software packages:

* Python 2.7.X (Python 3 is not currently supported)
* Boost::Python
* Matplotlib
* xerces C++ 3.1.1
* GEANT4.9.5
* g4py
* ROOT 5.32

For development, we also recommend:

* nose (to run unit tests)
* coverage (to measure the source coverage of the tests)
* pylint (to check for common problems in Python code)
* sphinx 1.1 dev or later (to generate the documentation with mathjax support)

We will explain how to install all of these packages in the following section.

Step-by-Step Installation: Ubuntu 11.10
---------------------------------------

Although Gnomon can run on any CUDA-supported Linux distribution or
Mac OS X, we strongly recommend the use of Ubuntu 11.10 for Gnomon
testing and development.  For these instructions, we will assume you
are starting with a fresh Ubuntu 11.10 installation.

Steps 1 and 2 will require root privileges, but the remaining steps
will be done in your home directory without administrator
intervention.


Step 1: ``apt-get`` packages from Ubuntu package manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Many packages are required to setup your build environment to compile
GEANT4 and ROOT.  Fortunately, they can be installed with one very
long ``apt-get`` line.  Although this line may wrap in your browser,
it should be executed as one line::

  sudo apt-get install build-essential xorg-dev python-dev \
       python-virtualenv python-numpy python-pygame libglu1-mesa-dev \
       glutg3-dev cmake uuid-dev liblapack-dev mercurial \
       libboost-all-dev libatlas-base-dev

To be able to generate the documentation, we also need these tools::

  sudo apt-get install texlive dvipng

.. warning:: For mac, sudo port install cmake, sudo easy_install virtualenv mercurial, sudo port install boost +python27


Step 2: virtualenv
^^^^^^^^^^^^^^^^^^

The excellent `virtualenv <http://www.virtualenv.org/>`_ tool
allows you to create an isolated Python environment, independent from
your system environment. We will keep all of the python modules for
Gnomon (with a few exceptions) and libraries compiled from source
inside of a virtualenv in your ``$HOME`` directory::

  virtualenv $HOME/env/gnomon
  cd $HOME/env/gnomon

Next, append the following lines to the end of
``$HOME/env/gnomon/bin/activate`` to allow codes to see locally installed libraries::

  export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
  export DYLD_LIBRARY_PATH=$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
  export PYTHONPATH=$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH


Finally, we can enable the virtual environment::

  source $HOME/env/gnomon/bin/activate

This will put the appropriate version of python in the path and also
set the ``$VIRTUAL_ENV`` environment variable we will use in the
remainder of the directions.

Step 3: ROOT
^^^^^^^^^^^^

Gnomon uses the ROOT I/O system to record event information to disk
for access later.  In addition, we expect many Gnomon users will
want to use ROOT to analyze the output of Gnomon.

Begin by downloading the ROOT 5.30 tarball from `the ROOT download
page <http://root.cern.ch/drupal/content/production-version-530>`_.
As of this writing, the latest version is 5.30.04.  Then, from the
download directory, execute the following commands::

  tar xvf root_v5.30.04.source.tar.gz
  mkdir $VIRTUAL_ENV/src/
  mv root $VIRTUAL_ENV/src/root-5.30.04
  cd $VIRTUAL_ENV/src/root-5.30.04
  ./configure
  make

We also need to append a ``source`` line to ``$VIRTUAL_ENV/bin/activate``::

  source $VIRTUAL_ENV/src/root-5.30.04/bin/thisroot.sh

Step 4: xerces c++
^^^^^^^^^^^^^^^^^^^^^^^^

Gnomon uses xerces to help Geant4 with parsing XML that is
used in our GDML geometry representation.  Proceed to the `xerces
C++ download page <http://xerces.apache.org/xerces-c/download.cgi>`_
and get version 3.1.1.

Proceed to your download directory then run the following commands::

  tar xvf xerces-c-3.1.1.tar.gz
  mv xerces-c-3.1.1 $VIRTUAL_ENV/src/
  cd $VIRTUAL_ENV/src/xerces-c-3.1.1
  ./configure --prefix=$VIRTUAL_ENV
  make install


.. warning:: If using Mac OS X, then xerces gets confused about the architecture.  It may be necessary to append ``CFLAGS="-arch x86_64" CXXFLAGS="-arch x86_64`` to the configure command.



Step 5: GEANT4
^^^^^^^^^^^^^^^^^^^^^^^^

Gnomon uses GEANT4 to model particle interactions with matter. These
instructions describe how to compile GEANT4 using the new CMake-based
build system.  As of GEANT4.9.5, CLHEP is shipped within GEANT4 along
with various data files which means it is no longer necessary to download
these on one's own.
  
Now go to the `GEANT4 Download Page <http://geant4.cern.ch/support/download.shtml>`_ and download the source code.

Next go to your download directory and run the following commands::

  tar xvf geant4.9.5.tar.gz
  mv geant4.9.5 $VIRTUAL_ENV/src/
  cd $VIRTUAL_ENV/src/
  mkdir geant4.9.5-build
  cd geant4.9.5-build
  cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV -DGEANT4_INSTALL_DATA=True -DGEANT4_USE_OPENGL_X11:BOOL=ON -DGEANT4_USE_GDML:BOOL=ON ../geant4.9.5
  make install


Step 6: g4py
^^^^^^^^^^^^

To access GEANT4 from Python, Gnomon uses the g4py wrappers.  We have
had to fix a few bugs and add wrapper a few additional classes for
Gnomon, so for now you will need to use our fork of g4py::

  cd $VIRTUAL_ENV/src
  hg clone https://bitbucket.org/tunnell/g4py
  cd g4py
  # select system name from linux, linux64, macosx as appropriate
  ./configure linux64 --with-g4-incdir=$VIRTUAL_ENV/include/Geant4 --with-g4-libdir=$VIRTUAL_ENV/lib --with-python-libdir=/usr/lib --with-boost-libdir=/usr/lib
  make
  make install


Now you can enable the Gnomon environment whenever you want by typing
``source $HOME/env/gnomon/bin/activate``, or by placing that line in the
``.bashrc`` login script.
