type HeroSectionProps = {
  header: string
  description?: string
}

export function HeroSection(props: HeroSectionProps) {
  const { header, description } = props
  return (
    <div>
      <section className="py-16 text-white hero bg-gradient-to-r from-purple-500 via-pink-500 to-red-500">
        <div className="container mx-auto text-center">
          <h1 className="mb-4 text-4xl font-bold">{header}</h1>
          {description ?
            <p className="text-lg font-light">
              {description}
            </p> : null}
        </div>
      </section>
    </div>
  )
}