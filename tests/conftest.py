def pytest_addoption(parser):
    parser.addoption("--parl", action="store", default='federal')


def pytest_generate_tests(metafunc):
    option_value = metafunc.config.option.parl
    if 'parl' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("parl", [option_value])
        print(option_value)