type FooterProps = {
  year?: number
  blogName?: string
  additionalText?: string
  textColor?: string
}

export function Footer(props: FooterProps) {
  const { year, blogName, additionalText, textColor } = props
  return (
    <div className="container mx-auto mt-20 text-center">
      <p className={`text-sm ${textColor}`}>
        © {year} {blogName}. {additionalText}
      </p>
    </div>
  )
}

export function SuperFooter(props: FooterProps) {
  const { year, blogName, additionalText, textColor } = props
  return (
    <div className="container mx-auto mt-20 text-center">
      <p className={`text-xl ${textColor}`}>
        © {year} {blogName}. {additionalText}
      </p>
    </div>
  )
}
