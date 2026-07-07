export default function SettingsPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Settings</h1>
        <p className="text-sm text-ink-muted mt-1">
          Workspace and notification preferences.
        </p>
      </div>

      <div className="rounded-lg border border-border bg-surface p-6 shadow-soft space-y-4">
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div>
            <p className="text-sm font-medium text-ink">Decision alerts</p>
            <p className="text-xs text-ink-muted mt-0.5">
              Get notified when the decision engine finds a high-confidence recommendation.
            </p>
          </div>
          <span className="text-xs text-ink-muted">Enabled</span>
        </div>
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div>
            <p className="text-sm font-medium text-ink">Default region</p>
            <p className="text-xs text-ink-muted mt-0.5">
              Stores shown by default across the platform.
            </p>
          </div>
          <span className="text-xs text-ink-muted">South Region</span>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-ink">Report cadence</p>
            <p className="text-xs text-ink-muted mt-0.5">
              How often the decision engine generates executive reports.
            </p>
          </div>
          <span className="text-xs text-ink-muted">Daily</span>
        </div>
      </div>
    </div>
  );
}
