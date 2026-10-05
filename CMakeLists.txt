include(cmake/FetchUpstream.cmake)
file(GLOB_RECURSE sources CONFIGURE_DEPENDS "${module}/src/*.cpp")
AddPlugin(mod-mythic-plus SOURCES ${sources} plugin/plugin.cpp)
target_include_directories(mod-mythic-plus PRIVATE "${module}/src" "${module}/src/Event" "${module}/src/Creature")
add_custom_target(mod-mythic-plus-upstream-files
  COMMAND ${CMAKE_COMMAND} -E copy_directory "${module}/conf" "${AC_PLUGINS_OUTPUT_DIR}/mod-mythic-plus/conf"
  COMMAND ${CMAKE_COMMAND} -E copy_directory "${module}/data" "${AC_PLUGINS_OUTPUT_DIR}/mod-mythic-plus/data"
  DEPENDS mod-mythic-plus-files VERBATIM)
add_dependencies(mod-mythic-plus mod-mythic-plus-upstream-files)
