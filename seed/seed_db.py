import os
import sys
import json
import uuid
from PIL import Image, ImageDraw

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.show import Show, ContentStatus
from app.models.season import Season
from app.models.episode import Episode
from app.auth.password import hash_password


def generate_sample_artwork():
    """Generates valid sample artwork image files in storage/artwork if missing."""
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../storage/artwork"))
    os.makedirs(storage_dir, exist_ok=True)

    artworks = [
        ("breaking_badlands_poster.jpg", 600, 900, (180, 40, 40), "Breaking Badlands"),
        ("breaking_badlands_banner.jpg", 1280, 720, (140, 30, 30), "Breaking Badlands Banner"),
        ("bb_trailer_thumb.jpg", 640, 360, (200, 50, 50), "Trailer Thumb"),
        ("bb_101_thumb.jpg", 640, 360, (150, 40, 40), "Pilot Thumb"),
        ("bb_102_thumb.jpg", 640, 360, (130, 35, 35), "Cat's in Bag Thumb"),
        ("cyberpunk_poster.jpg", 600, 900, (30, 140, 180), "Cyberpunk 2099"),
        ("cyberpunk_banner.jpg", 1280, 720, (20, 100, 150), "Cyberpunk Banner"),
        ("cp_101_thumb.jpg", 640, 360, (40, 120, 160), "Neon Awakening Thumb"),
    ]

    for fname, w, h, color, label in artworks:
        fpath = os.path.join(storage_dir, fname)
        if not os.path.exists(fpath):
            img = Image.new("RGB", (w, h), color=color)
            draw = ImageDraw.Draw(img)
            draw.text((w // 4, h // 2), label, fill=(255, 255, 255))
            img.save(fpath, "JPEG", quality=85)
            print(f"Generated sample artwork: {fname}")


def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Users
        admin_user = db.query(User).filter(User.email == "admin@peblo.tv").first()
        if not admin_user:
            admin_user = User(
                email="admin@peblo.tv",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
                full_name="Platform Admin"
            )
            db.add(admin_user)
            print("Created Admin User: admin@peblo.tv / admin123")

        editor_user = db.query(User).filter(User.email == "editor@peblo.tv").first()
        if not editor_user:
            editor_user = User(
                email="editor@peblo.tv",
                password_hash=hash_password("editor123"),
                role=UserRole.EDITOR,
                full_name="Content Editor"
            )
            db.add(editor_user)
            print("Created Editor User: editor@peblo.tv / editor123")

        db.commit()

        # 2. Seed Shows & Episodes
        seed_shows_path = os.path.join(os.path.dirname(__file__), "seed_shows.json")
        if os.path.exists(seed_shows_path):
            with open(seed_shows_path, "r", encoding="utf-8") as f:
                shows_data = json.load(f)

            for show_item in shows_data:
                existing_show = db.query(Show).filter(Show.title == show_item["title"]).first()
                if existing_show:
                    print(f"Show '{show_item['title']}' already exists. Skipping.")
                    continue

                show = Show(
                    title=show_item["title"],
                    synopsis=show_item.get("synopsis"),
                    category=show_item.get("category"),
                    section=show_item.get("section"),
                    status=ContentStatus(show_item.get("status", "draft")),
                    poster_url=show_item.get("poster_url"),
                    banner_url=show_item.get("banner_url"),
                )
                db.add(show)
                db.flush()

                for season_item in show_item.get("seasons", []):
                    season = Season(
                        show_id=show.id,
                        season_number=season_item["season_number"],
                        title=season_item.get("title"),
                        status=ContentStatus(season_item.get("status", "draft")),
                    )
                    db.add(season)
                    db.flush()

                    for ep_item in season_item.get("episodes", []):
                        ep = Episode(
                            season_id=season.id,
                            episode_number=ep_item["episode_number"],
                            title=ep_item["title"],
                            synopsis=ep_item.get("synopsis"),
                            duration_seconds=ep_item.get("duration_seconds"),
                            content_group=ep_item["content_group"],
                            language=ep_item.get("language", "English"),
                            status=ContentStatus(ep_item.get("status", "draft")),
                            thumbnail_url=ep_item.get("thumbnail_url"),
                            poster_url=ep_item.get("poster_url"),
                            banner_url=ep_item.get("banner_url"),
                        )
                        db.add(ep)

                print(f"Imported show: {show.title}")

            db.commit()
            print("Database seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_sample_artwork()
    seed_database()
