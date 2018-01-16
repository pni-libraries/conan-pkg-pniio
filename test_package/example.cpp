#include <iostream>
#include <pni/core.hpp>
#include <pni/io/nexus.hpp>
#include <h5cpp/hdf5.hpp>

using namespace pni::core;
using namespace pni::io;

int main()
{
	hdf5::file::File nexus_file = nexus::create_file("test.nxs",hdf5::file::AccessFlags::TRUNCATE);
	std::cout<<type_id_t::FLOAT32<<std::endl;

	return 0;
}
