export default function Button({
  variant = "primary",
  className = "",
  ...props
}) {
  const classes = ["ui-button", `ui-button-${variant}`, className]
    .filter(Boolean)
    .join(" ");

  return <button className={classes} {...props} />;
}
