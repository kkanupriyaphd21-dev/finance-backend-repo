package x.y.z;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface C004 extends JpaRepository<Entry, Long> {
}
