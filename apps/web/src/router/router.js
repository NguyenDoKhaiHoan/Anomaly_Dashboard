import { renderShell, bindShellEvents } from "../layout/app-shell";
import { getAuthState, refreshAuth } from "../state/auth-state";
import { renderLoginPage, bindLoginPage, renderRegisterPage, bindRegisterPage } from "../pages/auth-pages";
import { renderStreamingPage, bindStreamingPage } from "../pages/streaming-page";
import { renderHistoryPage, bindHistoryPage } from "../pages/history-page";
import { renderAlertsPage, bindAlertsPage } from "../pages/alerts-page";
import { renderModelMonitorPage, bindModelMonitorPage } from "../pages/model-monitor-page";
import { renderDatasetsPage, bindDatasetsPage } from "../pages/datasets-page";
import { renderModelsPage, bindModelsPage } from "../pages/models-page";
import { renderUsersPage, bindUsersPage } from "../pages/users-page";
import { renderProfilePage, bindProfilePage } from "../pages/profile-page";

let rootEl = null;
let cleanup = null;

const routeMap = {
  "/login": { guestOnly: true, render: renderLoginPage, bind: () => bindLoginPage(navigate, refreshAuth) },
  "/register": { guestOnly: true, render: renderRegisterPage, bind: () => bindRegisterPage(navigate) },
  "/dashboard/streaming": { auth: true, render: renderStreamingPage, bind: bindStreamingPage },
  "/dashboard/history": { auth: true, render: renderHistoryPage, bind: bindHistoryPage },
  "/dashboard/alerts": { auth: true, render: renderAlertsPage, bind: bindAlertsPage },
  "/dashboard/models": { auth: true, render: renderModelMonitorPage, bind: bindModelMonitorPage },
  "/admin/datasets": { auth: true, adminOnly: true, render: renderDatasetsPage, bind: bindDatasetsPage },
  "/admin/models": { auth: true, adminOnly: true, render: renderModelsPage, bind: bindModelsPage },
  "/admin/users": { auth: true, adminOnly: true, render: renderUsersPage, bind: bindUsersPage },
  "/profile": { auth: true, render: renderProfilePage, bind: bindProfilePage },
};

function normalizePath(pathname) {
  if (pathname === "/") return "/dashboard/streaming";
  return pathname;
}

function bindLinkInterceptor() {
  rootEl.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const link = target.closest("[data-link]");
    if (!link) return;
    event.preventDefault();
    const href = link.getAttribute("href");
    if (href) navigate(href);
  });
}

export async function renderCurrentRoute() {
  if (cleanup) {
    cleanup();
    cleanup = null;
  }

  const path = normalizePath(window.location.pathname);
  const route = routeMap[path];
  const auth = getAuthState();

  if (!route) {
    navigate("/dashboard/streaming", true);
    return;
  }
  if (route.auth && !auth.user) {
    navigate("/login", true);
    return;
  }
  if (route.guestOnly && auth.user) {
    navigate("/dashboard/streaming", true);
    return;
  }
  if (route.adminOnly && !auth.user?.is_superuser) {
    navigate("/dashboard/streaming", true);
    return;
  }

  const pageHtml = route.render();
  if (route.auth) {
    rootEl.innerHTML = renderShell(pageHtml, path);
    bindShellEvents(navigate);
  } else {
    rootEl.innerHTML = pageHtml;
  }
  const maybeCleanup = route.bind?.();
  if (typeof maybeCleanup === "function") cleanup = maybeCleanup;
}

export function navigate(path, replace = false) {
  if (replace) history.replaceState({}, "", path);
  else history.pushState({}, "", path);
  renderCurrentRoute();
}

export async function initRouter(root) {
  rootEl = root;
  bindLinkInterceptor();
  await refreshAuth();
  await renderCurrentRoute();
  window.addEventListener("popstate", renderCurrentRoute);
}
