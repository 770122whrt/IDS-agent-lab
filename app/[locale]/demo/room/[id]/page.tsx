import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { isLocale, locales, type Locale } from "@/i18n/config";
import enMessages from "@/i18n/messages/en.json";
import zhMessages from "@/i18n/messages/zh.json";

const imageData = [
  {
    id: "1",
    src: "/p1.JPEG",
    alt: "furniture goods 1",
    captionKey: "caption1",
  },
  {
    id: "2",
    src: "/p2.PNG",
    alt: "furniture goods 2",
    captionKey: "caption2",
  },
  {
    id: "3",
    src: "/p3.png",
    alt: "furniture goods 3",
    captionKey: "caption3",
  },
] as const;

const messagesByLocale = {
  zh: zhMessages,
  en: enMessages,
} satisfies Record<Locale, Record<string, unknown>>;

interface PageProps {
  params: Promise<{ locale: string; id: string }>;
}

function t(locale: Locale, key: string, params?: Record<string, string | number>) {
  const value = key.split(".").reduce<unknown>((current, part) => {
    if (current && typeof current === "object" && part in current) {
      return (current as Record<string, unknown>)[part];
    }
    return undefined;
  }, messagesByLocale[locale]);

  if (typeof value !== "string") {
    return key;
  }

  if (!params) {
    return value;
  }

  return value.replace(/\{(\w+)\}/g, (match, paramKey: string) => {
    return paramKey in params ? String(params[paramKey]) : match;
  });
}

export default async function RoomPage({ params }: PageProps) {
  const { locale: rawLocale, id } = await params;
  if (!isLocale(rawLocale)) {
    notFound();
  }

  const locale = rawLocale;
  const image = imageData.find((item) => item.id === id);

  if (!image) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-4xl px-4">
        <h1 className="mb-8 text-center text-3xl font-bold text-gray-800">
          {t(locale, "demo.detailTitle", { id })}
        </h1>

        <div className="rounded-lg bg-white p-6 shadow-lg">
          <div className="mb-6 text-center">
            <Image
              src={image.src}
              alt={image.alt}
              width={800}
              height={400}
              className="mx-auto rounded-lg shadow-md"
              priority
            />
            <p className="mt-4 text-sm text-gray-500">
              {t(locale, `demo.items.${image.captionKey}`)}
            </p>
          </div>

          <div className="mt-8 flex justify-between">
            {parseInt(id, 10) > 1 && (
              <Link
                href={`/${locale}/demo/room/${parseInt(id, 10) - 1}`}
                className="rounded bg-blue-600 px-6 py-2 text-white transition hover:bg-blue-700"
              >
                {t(locale, "demo.previous")}
              </Link>
            )}

            {parseInt(id, 10) < imageData.length && (
              <Link
                href={`/${locale}/demo/room/${parseInt(id, 10) + 1}`}
                className="ml-auto rounded bg-blue-600 px-6 py-2 text-white transition hover:bg-blue-700"
              >
                {t(locale, "demo.next")}
              </Link>
            )}
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="mb-2 text-gray-600">{t(locale, "demo.quickJump")}:</p>
          <div className="flex justify-center space-x-2">
            {imageData.map((item) => (
              <Link
                key={item.id}
                href={`/${locale}/demo/room/${item.id}`}
                className={`rounded px-3 py-1 ${
                  item.id === id ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                {t(locale, "demo.image", { id: item.id })}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function generateStaticParams() {
  return locales.flatMap((locale) =>
    imageData.map((item) => ({
      locale,
      id: item.id,
    })),
  );
}

export async function generateMetadata({ params }: PageProps) {
  const { locale: rawLocale, id } = await params;
  const locale = isLocale(rawLocale) ? rawLocale : "zh";

  return {
    title: t(locale, "demo.metadataTitle", { id }),
    description: t(locale, "demo.metadataDescription", { id }),
  };
}
