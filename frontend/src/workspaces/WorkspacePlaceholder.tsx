import "./workspace.css";

type WorkspacePlaceholderProps = {
  title: string;
  eyebrow: string;
  intent: string;
  guidance?: string;
};

export default function WorkspacePlaceholder({
  title,
  eyebrow,
  intent,
  guidance,
}: WorkspacePlaceholderProps) {
  return (
    <section className="workspace-placeholder" aria-labelledby="workspace-title">
      <p className="workspace-eyebrow">{eyebrow}</p>
      <h2 id="workspace-title">{title}</h2>
      <p className="workspace-intent">{intent}</p>
      <div className="workspace-frame" aria-label={`${title} guidance`}>
        <span>{guidance ?? "Nothing to show here yet."}</span>
      </div>
    </section>
  );
}
