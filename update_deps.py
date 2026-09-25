with open("packages/backend/src/backend/dependencies.py", "r", encoding="utf-8") as f:
    content = f.read()

new_dep = """

async def get_add_flashcard_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    authorization_service: AuthorizationService = Depends(get_authorization_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
):
    from application.learning.add_flashcard import AddFlashcardUseCase
    return AddFlashcardUseCase(
        auth_service=auth_service,
        authorization_service=authorization_service,
        uow_factory=uow_factory,
    )

async def get_get_learning_materials_use_case("""

content = content.replace("\nasync def get_get_learning_materials_use_case(", new_dep)

with open("packages/backend/src/backend/dependencies.py", "w", encoding="utf-8") as f:
    f.write(content)
