import Link from "next/link"

type SideBarProps = {
  name: string
  items: {
    name: string
    url: string
  }[]
}

export default function SideBar(props: SideBarProps) {
  const { name, items } = props
  return (
    <div>
      <aside className="container p-6 mx-auto mb-12 rounded-lg shadow-lg sidebar">
        <h2 className="mb-4 text-xl font-semibold">{name}</h2>
        <ul className="space-y-2">
          {items.map(item => {
            return <li key={item.name} className="transition duration-300 cursor-pointer hover:text-blue-500">
              <Link href={item.url}>
                {item.name}
              </Link>
            </li>
          })}
        </ul>
      </aside>
    </div>

  )

} 