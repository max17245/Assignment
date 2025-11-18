plugins {
    java
    application
}

group = "com.example"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    // Known vulnerable versions (for SCA testing only!)
    implementation("org.apache.logging.log4j:log4j-core:${property("log4jVersion")}")
    implementation("commons-collections:commons-collections:${property("commonsCollectionsVersion")}")
}

application {
    // Dummy main class (you don't even need to implement it for SCA)
    mainClass.set("com.example.App")
}
