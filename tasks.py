from invoke import run, task


@task
def compile_bootstrap():
    run(
        "lessc bootstrap_less/bootstrap.less djangit/static/css/bootstrap-djangit.css;"
    )

    print("Done.")
