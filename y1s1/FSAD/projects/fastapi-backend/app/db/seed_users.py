"""
Seed script to create default users for development.

This script creates default users (admin, teacher, student, etc.) if they don't already exist.
Useful for local development and testing.

Run with: python -m app.db.seed_users
"""

import bcrypt
from loguru import logger
from sqlmodel import Session, select

from app.db.session import engine
from app.models.user import User, UserRole


def create_default_users() -> None:
    """Create default users if they don't already exist."""
    
    default_users = [
        {
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@test.com",
            "password": "admin123",
            "role": UserRole.admin,
            "is_approved": True,
        },
        {
            "first_name": "John",
            "last_name": "Teacher",
            "email": "teacher@test.com",
            "password": "teacher123",
            "role": UserRole.teacher,
            "is_approved": True,
        },
        {
            "first_name": "Jane",
            "last_name": "Student",
            "email": "student@test.com",
            "password": "student123",
            "role": UserRole.student,
            "is_approved": True,
        },
        {
            "first_name": "Bob",
            "last_name": "Instructor",
            "email": "instructor@test.com",
            "password": "instructor123",
            "role": UserRole.instructor,
            "is_approved": True,
        },
        {
            "first_name": "Guest",
            "last_name": "User",
            "email": "guest@test.com",
            "password": "guest123",
            "role": UserRole.guest,
            "is_approved": True,
        },
    ]
    
    with Session(engine) as session:
        created_count = 0
        skipped_count = 0
        
        for user_data in default_users:
            # Check if user already exists
            existing_user = session.exec(
                select(User).where(User.email == user_data["email"])
            ).first()
            
            if existing_user:
                logger.info(f"User {user_data['email']} already exists, skipping...")
                skipped_count += 1
                continue
            
            # Hash the password
            password = user_data.pop("password")
            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")
            
            # Create new user
            new_user = User(
                **user_data,
                hashed_password=hashed_password,
            )
            
            session.add(new_user)
            logger.info(f"✓ Created user: {new_user.email} ({new_user.role})")
            created_count += 1
        
        # Commit all changes
        session.commit()
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Seeding complete!")
        logger.info(f"Created: {created_count} users")
        logger.info(f"Skipped: {skipped_count} users (already exist)")
        logger.info(f"{'='*50}\n")
        
        if created_count > 0:
            logger.info("Default User Credentials:")
            logger.info("-" * 50)
            for user_data in default_users:
                # Note: password was popped, so we need to reference the original
                passwords = {
                    "admin@test.com": "admin123",
                    "teacher@test.com": "teacher123",
                    "student@test.com": "student123",
                    "instructor@test.com": "instructor123",
                    "guest@test.com": "guest123",
                }
                email = user_data["email"]
                logger.info(f"  {user_data['role']:12} | {email:25} | {passwords[email]}")
            logger.info("-" * 50)


if __name__ == "__main__":
    logger.info("Starting database seeding...")
    create_default_users()
    logger.info("Database seeding finished!")
