package com.example.frontend;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
public class ApiController {

    private final RestTemplate restTemplate;
    private final String userServiceUrl;
    private final String productServiceUrl;

    public ApiController(RestTemplate restTemplate,
                         @Value("${user.service.url}") String userServiceUrl,
                         @Value("${product.service.url}") String productServiceUrl) {
        this.restTemplate = restTemplate;
        this.userServiceUrl = userServiceUrl;
        this.productServiceUrl = productServiceUrl;
    }

    @GetMapping(value = "/api/users", produces = MediaType.APPLICATION_JSON_VALUE)
    public String users() {
        return restTemplate.getForObject(userServiceUrl + "/users", String.class);
    }

    @GetMapping(value = "/api/products", produces = MediaType.APPLICATION_JSON_VALUE)
    public String products() {
        return restTemplate.getForObject(productServiceUrl + "/products", String.class);
    }

    @GetMapping("/health")
    public String health() {
        return "UP";
    }
}
