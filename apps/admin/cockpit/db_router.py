class WarehouseRouter:
    """Keep operational truth reads isolated from Django-owned auth tables."""

    route_app_labels = {"coverage"}

    def db_for_read(self, model, **_hints):
        return "warehouse" if model._meta.app_label in self.route_app_labels else None

    def db_for_write(self, model, **_hints):
        return "warehouse" if model._meta.app_label in self.route_app_labels else None

    def allow_migrate(self, db, app_label, **_hints):
        if app_label in self.route_app_labels:
            return False
        return db == "default"
