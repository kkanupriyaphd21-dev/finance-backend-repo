package x.y.z;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/entries")
public class C003 {

    private final com.example.core.data.EntryRepository repo;

    public C003(com.example.core.data.EntryRepository repo) {
        this.repo = repo;
    }

    @GetMapping
    public ResponseEntity<List<com.example.core.data.Entry>> list() {
        return ResponseEntity.ok(repo.findAll());
    }

    @PostMapping
    public ResponseEntity<com.example.core.data.Entry> create(@RequestBody com.example.core.data.Entry entry) {
        com.example.core.data.Entry saved = repo.save(entry);
        return ResponseEntity.ok(saved);
    }
}
