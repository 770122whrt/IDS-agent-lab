import React from 'react'
import Link from 'next/link'

function ShopPage() {
  const images = [
    { id: '1', title: 'Modern sofa', description: 'High quality modern style sofa' },
    { id: '2', title: 'office desks and chairs', description: 'Comfortable office furniture set' },
    { id: '3', title: 'bedroom furniture', description: 'Warm bedroom furniture combination' }
  ]

  return (
    <div className="min-h-screen py-8 bg-gray-50">
      <div className="max-w-6xl px-4 mx-auto">
        <h1 className="mb-8 text-lg font-bold text-center text-gray-800 lg:text-4xl">
          Product Display
        </h1>
        <p className="mb-12 text-lg text-center text-gray-600">
          Click on the image below to view product details
        </p>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
          {images.map((image) => (
            <Link
              key={image.id}
              href={`/shop/room/${image.id}`}
              className="block overflow-hidden transition duration-300 bg-white rounded-lg shadow-lg hover:shadow-xl"
            >
              <div className="bg-gray-200 aspect-w-16 aspect-h-9">
                <div className="flex items-center justify-center w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100">
                  <span className="text-2xl font-bold text-gray-700">image {image.id}</span>
                </div>
              </div>
              <div className="p-6">
                <h3 className="mb-2 text-xl font-semibold text-gray-800">{image.title}</h3>
                <p className="text-gray-600">{image.description}</p>
                <div className="mt-4 font-medium text-blue-600">View details →</div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ShopPage