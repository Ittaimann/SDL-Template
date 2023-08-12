#!/usr/bin/python3
import os
import subprocess

CMAKE_TEMPLATE = """
cmake_minimum_required(VERSION %CMAKE_VERSION%)

project(%REPO_NAME%)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_subdirectory(external/SDL)
add_executable(%REPO_NAME% main.cpp)
target_include_directories(%REPO_NAME% PUBLIC external/SDL/include)

if(MSVC)
    set_property(DIRECTORY ${PROJECT_ROOT} PROPERTY VS_STARTUP_PROJECT ${PROJECT_NAME})
endif()
if(TARGET SDL2::SDL2main)
    # It has an implicit dependency on SDL2 functions, so it MUST be added before SDL2::SDL2 (or SDL2::SDL2-static)
    target_link_libraries(%REPO_NAME% PRIVATE SDL2::SDL2main)
endif()
target_link_libraries(%REPO_NAME% PRIVATE SDL2-static)
"""

MAIN_CPP_TEMPLATE= """
//SDL2 Template project from : https://trenki2.github.io/blog/2017/06/02/using-sdl2-with-cmake/
#include <SDL.h> 

int main(int argc, char *argv[])
{
  SDL_Init(SDL_INIT_VIDEO);

  SDL_Window *window = SDL_CreateWindow(
    "SDL2Test",
    SDL_WINDOWPOS_UNDEFINED,
    SDL_WINDOWPOS_UNDEFINED,
    640,
    480,
    0
  );

  SDL_Renderer *renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);
  SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE);
  SDL_RenderClear(renderer);
  SDL_RenderPresent(renderer);

  SDL_Delay(3000);

  SDL_DestroyWindow(window);
  SDL_Quit();

  return 0;
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
    if(args.regen):
        generate()
    if(args.build):
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
        selection = input("Which generator?\n")
        if int(selection) in range(0, len(generators)):
            return generators[int(selection)]

if __name__ == "__main__":
    print("""Welcome the sdl bootstrapper! This is just to get started with sdl.
            This script will builds a cmake project and pull sdl2 for you!
            it will also set up a local git repo for you, but not the remote (no easy github (ಥ⌣ಥ))""")
    project_name = input("what is the name of your project?\n")
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
    cmake_list_txt.write(CMAKE_TEMPLATE.replace("%CMAKE_VERSION%",version).replace("%REPO_NAME%",project_name))
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

    subprocess.run([python_executable,"build.py", "-g", "-b"],cwd=project_path) 
    
