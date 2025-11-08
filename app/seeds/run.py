import typer
from app.seeds.service import run_users, run_categories, run_tags, run_all

app = typer.Typer(help="Seeds:users, categories, tags")


@app.command("all")
def all_():
    run_all()
    typer.echo("Todos los seeds creados")


@app.command("users")
def users():
    run_users()
    typer.echo("Usuarios Cargados")


@app.command("categories")
def categories():
    run_categories()
    typer.echo("Categorias Cargadas")


@app.command("tags")
def tags():
    run_tags()
    typer.echo("Tags Cargadas")
