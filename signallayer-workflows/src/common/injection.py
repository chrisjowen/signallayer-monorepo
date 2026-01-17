"""Dependency injection configuration."""

import inject

from ..worker.lib.registry import ActivityRegistry, WorkflowRegistry


def configure_inject():
    """Configure the shared dependency injection container."""
    def config(binder: inject.Binder):
        # Registries
        binder.bind_to_constructor(WorkflowRegistry, WorkflowRegistry)
        binder.bind_to_constructor(ActivityRegistry, ActivityRegistry)

        # Settings
        from ..web.config import WebSettings
        from ..worker.config import WorkerSettings

        from .config.github import GitHubSettings
        from .config.scrapingbee import ScrapingBeeSettings

        binder.bind_to_constructor(WorkerSettings, WorkerSettings)
        binder.bind_to_constructor(WebSettings, WebSettings)
        binder.bind_to_constructor(GitHubSettings, GitHubSettings)
        binder.bind_to_constructor(ScrapingBeeSettings, ScrapingBeeSettings)

        # External Clients
        from scrapingbee import ScrapingBeeClient  # type: ignore

        def provide_scrapingbee_client() -> ScrapingBeeClient:
            settings = ScrapingBeeSettings()
            return ScrapingBeeClient(api_key=settings.api_key)

        binder.bind_to_provider(ScrapingBeeClient, provide_scrapingbee_client)

        # Collaboration platform clients
        from .clients.github import GitHubClient
        from .clients.reddit import RedditClient

        binder.bind_to_constructor(GitHubClient, GitHubClient)
        binder.bind_to_constructor(RedditClient, RedditClient)

        # Contexts
        from ..contexts.collaboration import CollaborationContext

        binder.bind_to_constructor(CollaborationContext, CollaborationContext)

        # Example service
        from .dummy_service import DummyService

        binder.bind_to_constructor(DummyService, DummyService)

    if not inject.is_configured():
        inject.configure(config)
