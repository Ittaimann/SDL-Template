#!/usr/bin/python3
import os
import subprocess

CMAKE_TEMPALTE = """
cmake_minimum_required(VERSION %CMAKE_VERSION%)

project(%REPO_NAME%)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_subdirectory(external/SDL)
add_executable(%REPO_NAME% main.cpp)
target_include_directories(%REPO_NAME% PUBLIC external/SDL/include)
target_link_libraries(%REPO_NAME% SDL2)
"""

MAIN_CPP_TEMPLATE= """
#include<SDL.h>
#include <iostream>

int main()
{
    if(SDL_Init(SDL_INIT_VIDEO) < 0)
    {
        std::cout << "Failed to initialize the SDL2 library\\n";
        return -1;
    }

    SDL_Window *window = SDL_CreateWindow("SDL2 Window",
                                          SDL_WINDOWPOS_CENTERED,
                                          SDL_WINDOWPOS_CENTERED,
                                          680, 480,
                                          0);

    if(!window)
    {
        std::cout << "Failed to create window\\n";
        return -1;
    }

    SDL_Surface *window_surface = SDL_GetWindowSurface(window);

    if(!window_surface)
    {
        std::cout << "Failed to get the surface from the window\\n";
        return -1;
    }

    SDL_UpdateWindowSurface(window);

    SDL_Delay(5000);
}
"""

PYTHON_BUILD = """
import subprocess
import os
import argparse

GENERATOR_TEXT = "%GENERATOR%"

def generate():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    subprocess.run(["cmake", "-G",GENERATOR_TEXT,".."],cwd=os.path.join(dir_path,"build")) 
def build():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    subprocess.run(["cmake", "--build","." ],cwd=os.path.join(dir_path,"build")) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Short cuts for the build')

    parser.add_argument('-g', dest="regen", action="store_true", help='regenerate project with files with the original generator')
    parser.add_argument('-b', dest="build", action="store_true", help='builds project')

    args = parser.parse_args()
    if(args.regen != None):
        generate()
    if(args.build != None):
        build()

"""

def cleanup(gen_text):
    result = gen_text.split("=")[0]
    result = result.strip("*")
    result = result.strip()
    return result

def find_generators(generators_text):
    """
    return: list of generators
    """
    results = []
    for x in generators_text.split("\n")[3:]:
        if "=" in x:
            check = cleanup(x)
            if check != "":
                results.append(cleanup(x))
    return results

def print_generators(generators):
    for gen in generators:
        print(f"[{generators.index(gen)}]:{gen}")

def select_generator(generators):
    print("select your build system!, id suggest visual studio if you have windows and make or ninja for anything else")
    print_generators(generators)
    not_selected = True
    while not_selected:
        selection = input("Which generator?")
        if int(selection) in range(0, len(generators)):
            return generators[int(selection)]

if __name__ == "__main__":
    print("""Welcome the sdl bootstrapper! This is just to get started with sdl.
            This script will builds a cmake project and pull sdl2 for you!
            it will also set up a local git repo for you, but not the remote (no easy github (ಥ⌣ಥ))""")
    project_name = input("what is the name of your project?")
    version_text = subprocess.run(["cmake", "--version"], capture_output=True,text=True) 
    version = version_text.stdout.split("\n")[0].split(" ")[-1]

    generators_text = subprocess.run(["cmake", "--help"], capture_output=True,text=True).stdout.split("Generators")[1] 
    generators = find_generators(generators_text)

    generator = select_generator(generators)
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    project_path = os.path.join(dir_path,project_name) 

    os.mkdir(project_path)
    subprocess.run(["git", "init", project_name], capture_output=True,text=True) 

    os.mkdir(os.path.join(project_path,"build"))
    main_cpp = open(os.path.join(project_path, "main.cpp"),"x")
    main_cpp.write(MAIN_CPP_TEMPLATE)
    main_cpp.close()

    cmake_list_txt = open(os.path.join(project_path, "CMakeLists.txt"),"x")
    cmake_list_txt.write(CMAKE_TEMPALTE.replace("%CMAKE_VERSION%",version).replace("%REPO_NAME%",project_name))
    cmake_list_txt.close()

    git_ignore = open(os.path.join(project_path, ".gitignore"),"x")
    git_ignore.write("/build")
    git_ignore.close()
    
    os.mkdir(os.path.join(project_path,"external"))
    subprocess.run(["git","submodule","add","-b","release-2.28.x","https://github.com/libsdl-org/SDL.git"],cwd=os.path.join(project_path,"external")) 

    python_build= open(os.path.join(project_path, "build.py"),"x")
    python_build.write(PYTHON_BUILD.replace("%GENERATOR%",generator))
    python_build.close()

    python_executable="python3"    
    if os.name == 'nt':
        python_executable = "py" #pray

    subprocess.run([python_executable,"build.py", "-g"],cwd=project_path) 
    subprocess.run([python_executable,"build.py", "-b"],cwd=project_path) 
    
