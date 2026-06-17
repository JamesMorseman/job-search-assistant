import "./workspace.css";

type WorkspacePlaceholderProps = {
  title: string;
  eyebrow: string;
  intent: string;
};

export default function WorkspacePlaceholder({
  title,
  eyebrow,
  intent
}: WorkspacePlaceholderProps) {
  return (
    <section className="workspace-placeholder" aria-labelledby="workspace-title">
      <p className="workspace-eyebrow">{eyebrow}</p>
      <h2 id="workspace-title">{title}</h2>
      <p className="workspace-intent">{intent}</p>
      <div className="workspace-frame" aria-label={`${title} placeholder`}>
        <span>Placeholder surface</span>
      </div>
    </section>
  );
}
