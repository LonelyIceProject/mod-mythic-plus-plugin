include(FetchContent)
find_package(Git REQUIRED)
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/plugin.json" manifest)
string(JSON repo GET "${manifest}" source repo)
string(JSON commit GET "${manifest}" source commit)
file(GLOB patches CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/patches/*.patch")
set(patch_command "")
if(patches)
  set(patch_command PATCH_COMMAND "${GIT_EXECUTABLE}" reset --quiet --hard "${commit}"
    COMMAND "${GIT_EXECUTABLE}" clean --quiet -fd
    COMMAND "${GIT_EXECUTABLE}" apply --whitespace=nowarn ${patches})
endif()
FetchContent_Declare(mod_mythic_plus_upstream GIT_REPOSITORY "${repo}" GIT_TAG "${commit}"
  SOURCE_SUBDIR none ${patch_command})
FetchContent_MakeAvailable(mod_mythic_plus_upstream)
set(module "${mod_mythic_plus_upstream_SOURCE_DIR}")
