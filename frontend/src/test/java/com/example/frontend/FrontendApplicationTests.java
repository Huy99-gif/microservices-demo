package com.example.frontend;

import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class FrontendApplicationTests {

    @Autowired
    private ApiController apiController;

    @Test
    void contextLoads() {
        assertNotNull(apiController);
    }
}
