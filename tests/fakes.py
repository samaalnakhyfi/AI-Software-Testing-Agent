"""Minimal stand-ins for Playwright objects so the agent logic can be tested offline."""


class FakeLocator:
    def __init__(self, count):
        self._count = count

    def count(self):
        return self._count


class FakePage:
    def __init__(self, title="Example Domain", url="https://example.com/", links=("Learn more",)):
        self._title = title
        self.url = url
        self.links = list(links)

    def title(self):
        return self._title

    def locator(self, selector):
        return FakeLocator(len(self.links) if selector == "a" else 1)

    def get_by_role(self, role, name):
        return FakeLocator(sum(name.lower() in link.lower() for link in self.links))


class FakeResponse:
    def __init__(self, status=200):
        self.status = status
        self.ok = 200 <= status < 400
