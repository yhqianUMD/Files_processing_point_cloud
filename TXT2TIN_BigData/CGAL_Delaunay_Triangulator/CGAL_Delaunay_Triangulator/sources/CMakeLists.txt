# Created by the script cgal_create_CMakeLists
# This is the CMake script for compiling a set of CGAL applications.

cmake_minimum_required(VERSION 3.1...3.15)

project( dtri )


# CGAL and its components
find_package(CGAL REQUIRED PATHS /apps/cgal/4.9/lib64/CGAL)
set(CGAL_INCLUDE_DIR "/apps/cgal/4.9")
set(CGAL_LIBRARIES "/apps/cgal/4.9/lib64")
#~ CGAL_INCLUDE_DIR


# Boost and its components
set(BOOST_ROOT "/apps/boost/1.59.0")
set(BOOST_LIBRARYDIR "/apps/boost/1.59.0/lib")
#~ find_package(Boost REQUIRED)
#~ find_package(Doxygen REQUIRED)
#~ find_package( Boost REQUIRED )


# include for local directory

# include for local package


# Creating entries for target: dtri
# ############################

add_executable( dtri string_management.h string_management.cpp io.h io.cpp main_tri.cpp  )

#add_to_cached_list( CGAL_EXECUTABLE_TARGETS dtri )

# Link the executable to CGAL and third-party libraries
target_link_libraries(dtri CGAL::CGAL )

