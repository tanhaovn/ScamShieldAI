export default function Card({
  as: Element = "section",
  className = "",
  children,
  ...props
}) {
  const classes = ["ui-card", className].filter(Boolean).join(" ");

  return (
    <Element className={classes} {...props}>
      {children}
    </Element>
  );
}
