from invoke import task

@task
def test_core(c):
    c.run("cd core_system && pytest -s -vv --ds=core_system.test_settings.test")

@task
def test_hr(c):
    c.run("cd hr_system && pytest -s -vv --ds=hr_system.test_settings.test")

@task
def test_all(c):
    test_core(c)
    test_hr(c)
