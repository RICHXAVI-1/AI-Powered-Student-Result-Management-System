CREATE DATABASE result_management;

USE result_management;

CREATE TABLE `courses` (
   `id` int NOT NULL AUTO_INCREMENT,
   `course_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
   `course_title` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
   `credit_unit` int NOT NULL,
   `semester` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
   `level` int NOT NULL,
   `department_id` int NOT NULL,
   `created_at` datetime DEFAULT NULL,
   PRIMARY KEY (`id`),
   UNIQUE KEY `course_code` (`course_code`),
   KEY `department_id` (`department_id`),
   CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`)
 ) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci



CREATE TABLE `departments` (
   `id` int NOT NULL AUTO_INCREMENT,
   `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
   `code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
   `created_at` datetime DEFAULT NULL,
   PRIMARY KEY (`id`),
   UNIQUE KEY `code` (`code`)
 ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci




CREATE TABLE `results` (
   `id` int NOT NULL AUTO_INCREMENT,
   `student_id` int NOT NULL,
   `course_id` int NOT NULL,
   `session` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
   `score` float NOT NULL,
   `grade` varchar(2) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `grade_point` float DEFAULT NULL,
   `remarks` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
   `created_at` datetime DEFAULT NULL,
   `updated_at` datetime DEFAULT NULL,
   PRIMARY KEY (`id`),
   KEY `student_id` (`student_id`),
   KEY `course_id` (`course_id`),
   CONSTRAINT `results_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
   CONSTRAINT `results_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`)
 ) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci





CREATE TABLE `session_summaries` (
   `id` int NOT NULL AUTO_INCREMENT,
   `student_id` int NOT NULL,
   `session` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
   `semester` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
   `total_units` int DEFAULT NULL,
   `total_points` float DEFAULT NULL,
   `gpa` float DEFAULT NULL,
   `cgpa` float DEFAULT NULL,
   `created_at` datetime DEFAULT NULL,
   PRIMARY KEY (`id`),
   KEY `student_id` (`student_id`),
   CONSTRAINT `session_summaries_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
 ) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci





CREATE TABLE `students` (
   `id` int NOT NULL AUTO_INCREMENT,
   `matric_number` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
   `first_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
   `last_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
   `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
   `department_id` int NOT NULL,
   `level` int NOT NULL,
   `user_id` int DEFAULT NULL,
   `created_at` datetime DEFAULT NULL,
   PRIMARY KEY (`id`),
   UNIQUE KEY `matric_number` (`matric_number`),
   UNIQUE KEY `email` (`email`),
   KEY `department_id` (`department_id`),
   KEY `user_id` (`user_id`),
   CONSTRAINT `students_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
   CONSTRAINT `students_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
 ) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci




CREATE TABLE `users` (
   `id` int NOT NULL AUTO_INCREMENT,
   `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
   `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
   `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
   `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
   `created_at` datetime DEFAULT NULL,
   PRIMARY KEY (`id`),
   UNIQUE KEY `username` (`username`),
   UNIQUE KEY `email` (`email`)
 ) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci