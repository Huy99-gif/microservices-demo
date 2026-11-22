package com.example.user;

import java.util.List;

import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

/** Them du lieu mau neu bang users dang rong. */
@Component
public class DataSeeder implements ApplicationRunner {

    private final UserRepository repository;

    public DataSeeder(UserRepository repository) {
        this.repository = repository;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (repository.count() == 0) {
            repository.saveAll(List.of(
                    new User(null, "Nguyen Van A", "a@example.com"),
                    new User(null, "Tran Thi B", "b@example.com"),
                    new User(null, "Le Van C", "c@example.com")));
        }
    }
}
