type PageHeaderProps = {
  eyebrow?: string;
  title: string;
  description: string;
  trustItems?: string[];
  titleId?: string;
};

export function PageHeader({ eyebrow, title, description, trustItems = [], titleId = "page-title" }: PageHeaderProps) {
  return (
    <header className="page-intro" aria-labelledby={titleId}>
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <div className="intro-row">
        <div>
          <h1 id={titleId}>{title}</h1>
          <p className="intro-copy">{description}</p>
        </div>
        {trustItems.length > 0 && (
          <div className="trust-line" aria-label="Data principles">
            {trustItems.map((item) => <span key={item}>{item}</span>)}
          </div>
        )}
      </div>
    </header>
  );
}
