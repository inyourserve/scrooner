type PageHeaderProps = {
  eyebrow?: string;
  title: string;
  description: string;
  trustItems?: string[];
  titleId?: string;
  tone?: "product" | "editorial";
};

export function PageHeader({ eyebrow, title, description, trustItems = [], titleId = "page-title", tone = "product" }: PageHeaderProps) {
  return (
    <header className={`ds-page-header ds-page-header--${tone} page-intro`} aria-labelledby={titleId}>
      {eyebrow && <p className="ds-page-header__eyebrow eyebrow">{eyebrow}</p>}
      <div className="intro-row">
        <div>
          <h1 className="ds-page-header__title" id={titleId}>{title}</h1>
          <p className="ds-page-header__description intro-copy">{description}</p>
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
