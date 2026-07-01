"use client";

import Link from "next/link";
import { useLanguage } from "@/i18n/context/language-context";

export default function ShopPage() {
  const { t, locale } = useLanguage();
  const images = [
    { id: "1", title: t("demo.items.sofaTitle"), description: t("demo.items.sofaDescription") },
    { id: "2", title: t("demo.items.officeTitle"), description: t("demo.items.officeDescription") },
    { id: "3", title: t("demo.items.bedroomTitle"), description: t("demo.items.bedroomDescription") },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-6xl px-4">
        <h1 className="mb-8 text-center text-lg font-bold text-gray-800 lg:text-4xl">{t("demo.title")}</h1>
        <p className="mb-12 text-center text-lg text-gray-600">{t("demo.description")}</p>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
          {images.map((image) => (
            <Link
              key={image.id}
              href={`/${locale}/demo/room/${image.id}`}
              className="block overflow-hidden rounded-lg bg-white shadow-lg transition duration-300 hover:shadow-xl"
            >
              <div className="bg-gray-200 aspect-w-16 aspect-h-9">
                <div className="flex h-48 w-full items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100">
                  <span className="text-2xl font-bold text-gray-700">{t("demo.image", { id: image.id })}</span>
                </div>
              </div>
              <div className="p-6">
                <h3 className="mb-2 text-xl font-semibold text-gray-800">{image.title}</h3>
                <p className="text-gray-600">{image.description}</p>
                <div className="mt-4 font-medium text-blue-600">{t("demo.viewDetails")} -&gt;</div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
