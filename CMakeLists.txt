include(cmake/FetchUpstream.cmake)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(GLOB_RECURSE sources CONFIGURE_DEPENDS "${module}/src/*.cpp")
AddPlugin(mod-mythic-plus SOURCES ${sources} plugin/plugin.cpp)
target_include_directories(mod-mythic-plus PRIVATE "${module}/src" "${module}/src/Event" "${module}/src/Creature")
add_custom_target(mod-mythic-plus-upstream-files
  COMMAND ${CMAKE_COMMAND} -E copy_directory "${module}/conf" "${AC_PLUGINS_OUTPUT_DIR}/mod-mythic-plus/conf"
  COMMAND ${CMAKE_COMMAND} -E copy_directory "${module}/data" "${AC_PLUGINS_OUTPUT_DIR}/mod-mythic-plus/data"
  COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/cmake/adapt_sql.py" "${AC_PLUGINS_OUTPUT_DIR}/mod-mythic-plus/data"
  VERBATIM)
add_dependencies(mod-mythic-plus-upstream-files mod-mythic-plus-files)
add_dependencies(mod-mythic-plus mod-mythic-plus-upstream-files)

option(LONELYICE_PORT_TESTS "Build isolated package SQL validation tools" OFF)
if(LONELYICE_PORT_TESTS)
  add_executable(mythic-sql-check tests/sql-package.cpp)
  target_link_libraries(mythic-sql-check PRIVATE dbdialect common sqlite3 acore-core-interface)
endif()
