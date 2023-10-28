#!/usr/bin/python3
import os
import subprocess

SPLASH ="""
  ______   ______   _____      ______      ___      ___      ___    _________  ________  _______     
.' ____ \ |_   _ `.|_   _|    |_   _ \   .'   `.  .'   `.  .'   `. |  _   _  ||_   __  ||_   __ \    
| (___ \_|  | | `. \ | |        | |_) | /  .-.  \/  .-.  \/  .-.  \|_/ | | \_|  | |_ \_|  | |__) |   
 _.____`.   | |  | | | |   _    |  __'. | |   | || |   | || |   | |    | |      |  _| _   |  __ /    
| \____) | _| |_.' /_| |__/ |  _| |__) |\  `-'  /\  `-'  /\  `-'  /   _| |_    _| |__/ | _| |  \ \_  
 \______.'|______.'|________| |_______/  `.___.'  `.___.'  `.___.'   |_____|  |________||____| |___| 

"""

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
    SDL_WINDOW_SHOWN
  );

  SDL_Renderer *renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
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
        print(f"\t\t[{generators.index(gen)}]:{gen}")

def select_generator(generators):
    print_generators(generators)
    not_selected = True

    print("Select your build system!, id suggest visual studio if you have windows and make or ninja for anything else")
    while not_selected:
        selection = input("Which generator?\n")
        if int(selection) in range(0, len(generators)):
            print("(ﾉ◕ヮ◕)ﾉ*:・ﾟ✧")
            return generators[int(selection)]

if __name__ == "__main__":
    print(SPLASH)

    print("""
Welcome the silly sdl bootstrapper! This is just to get quickly started with sdl by doing a couple things
\t\t\t\t(*・‿・)ノ⌒*:･ﾟ✧ 
\t\t[1] Pulls the SDL library for you
\t\t[2] makes a git repo for you and sets up the submodules
\t\t[3] sets up a cmake project for you (minimally)
\t\t[4] builds and links the default main.cpp 
\t\t[5] Provides you with a build script you can run 	

Things I can't promise you:  
\t\t\t\t(╥﹏╥)
\t\t[1] You will have to select a generator which cmake may say is there... but isn't
\t\t[2] it might not build 
\t\t[3] cmake might not be actually proper
\t\t[4] won't teach you how cmake works
\t\t[5] won't work on every platform (not tested on macos)
\t\t[6] will likely break as I didn't really do any kind of protective programmings
\t\t[7] will by default only build in debug (experiment with the cmake, get those frames back!)
\t\t[8] won't set up your debugger or code completion tool 

Warnings: ಠ_ಠ
\t\t[1] This does make a new directory where it is run. Make sure the name is unique

Tiny notes:
\t\t[1] if on windows maybe try this script via the developer prompt
""")

    project_name = input("Lets get started! Whats you projects name (no spaces are crazy symbols pls)?\n")
    version_text = subprocess.run(["cmake", "--version"], capture_output=True,text=True) 
    version = version_text.stdout.split("\n")[0].split(" ")[-1]

    generators_text = subprocess.run(["cmake", "--help"], capture_output=True,text=True).stdout.split("Generators")[1] 
    generators_list = find_generators(generators_text)
    generator = select_generator(generators_list)
    
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
    print("And done! In order to run your executable look under the /build folder in your new project!")
    print(f"On windows, your executable will likely be under build/debug/{project_name}")
    print("windows anti virus may also throw a warning, but building the project should clear it")
    print("""
 __                         _       _            
/ _\ ___  ___ _   _  __ _  | | __ _| |_ ___ _ __ 
\ \ / _ \/ _ \ | | |/ _` | | |/ _` | __/ _ \ '__|
_\ \  __/  __/ |_| | (_| | | | (_| | ||  __/ |   
\__/\___|\___|\__, |\__,_| |_|\__,_|\__\___|_|   
              |___/
""")
