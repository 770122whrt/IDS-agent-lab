import Image from 'next/image'
import { notFound } from 'next/navigation'

// Define image data
const imageData = [
  {
    id: '1',
    src: '/p1.JPEG',
    alt: 'furniture goods 1',
    caption: 'Figure: photo1 - Beautiful furniture design'
  },
  {
    id: '2',
    src: '/p2.PNG',
    alt: 'furniture goods 2',
    caption: 'Figure: photo2 - Modern furniture collection'
  },
  {
    id: '3',
    src: '/p3.png',
    alt: 'furniture goods 3',
    caption: 'Figure: photo3 - Luxury furniture items'
  }
]

interface PageProps {
  params: Promise<{ id: string }>
}

async function RoomPage({ params }: PageProps) {
  // Unpack params
  const { id } = await params

  // Search for corresponding image data
  const image = imageData.find((item) => item.id === id)

  // If the image cannot be found, display 404
  if (!image) {
    notFound()
  }

  return (
    <div className="min-h-screen py-8 bg-gray-50">
      <div className="max-w-4xl px-4 mx-auto">
        <h1 className="mb-8 text-3xl font-bold text-center text-gray-800">Product Details - image {id}</h1>

        {/* Image display area */}
        <div className="p-6 bg-white rounded-lg shadow-lg">
          <div className="mb-6 text-center">
            <Image
              src={image.src}
              alt={image.alt}
              width={800}
              height={400}
              className="mx-auto rounded-lg shadow-md"
              priority
            />
            <p className="mt-4 text-sm text-gray-500">{image.caption}</p>
          </div>

          {/* Navigation button */}
          <div className="flex justify-between mt-8">
            {parseInt(id) > 1 && (
              <a
                href={`/shop/room/${parseInt(id) - 1}`}
                className="px-6 py-2 text-white transition bg-blue-600 rounded hover:bg-blue-700"
              >
                previous one
              </a>
            )}

            {parseInt(id) < imageData.length && (
              <a
                href={`/shop/room/${parseInt(id) + 1}`}
                className="px-6 py-2 ml-auto text-white transition bg-blue-600 rounded hover:bg-blue-700"
              >
                next one
              </a>
            )}
          </div>
        </div>

        {/* Quick Navigation */}
        <div className="mt-6 text-center">
          <p className="mb-2 text-gray-600">Quick Jump:</p>
          <div className="flex justify-center space-x-2">
            {imageData.map((item) => (
              <a
                key={item.id}
                href={`/shop/room/${item.id}`}
                className={`px-3 py-1 rounded ${item.id === id ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
              >
                image {item.id}
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Generate static path
export function generateStaticParams() {
  return imageData.map((item) => ({
    num: item.id
  }))
}

// Generate page metadata
export async function generateMetadata({ params }: PageProps) {
  const resolvedParams = await params
  const { id } = resolvedParams
  const image = imageData.find((item) => item.id === id)

  return {
    title: `product image ${id} - My store`,
    description: image?.caption ?? `product image ${id} 's Detailed Display`
  }
}

export default RoomPage
